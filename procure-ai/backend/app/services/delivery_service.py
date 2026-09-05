from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from typing import Dict, Any

from app.models.procurement import PurchaseOrder, PurchaseOrderItem, RFQItem
from app.models.advanced import DeliveryCommitment, RiskEvent
from app.models.sales import SalesOrder
from app.services import ai_extraction

def confirm_delivery(db: Session, po_id: uuid.UUID, data: Dict[str, Any]) -> DeliveryCommitment:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
        
    po_item = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.purchase_order_id == po_id).first()
    if not po_item:
        raise HTTPException(status_code=400, detail="PO has no items")
        
    # Update status
    po.status = "Confirmed"
    
    # Save commitment
    commit = DeliveryCommitment(
        purchase_order_item_id=po_item.id,
        quantity=data["confirmed_quantity"],
        committed_date=data.get("final_delivery_date") or data.get("first_delivery_date")
    )
    db.add(commit)
    db.flush()
    
    # Recalculate impact
    recalculate_delivery_impact(db, po_id, data["confirmed_quantity"], commit.committed_date)
    
    db.commit()
    db.refresh(commit)
    return commit

def confirm_delivery_from_email(db: Session, po_id: uuid.UUID, raw_text: str) -> DeliveryCommitment:
    extracted_data = ai_extraction.extract_delivery_from_email(raw_text)
    
    # ensure dates are datetime objects for insertion
    if isinstance(extracted_data.get("first_delivery_date"), str):
        extracted_data["first_delivery_date"] = datetime.fromisoformat(extracted_data["first_delivery_date"].replace('Z', '+00:00'))
    if isinstance(extracted_data.get("final_delivery_date"), str):
        extracted_data["final_delivery_date"] = datetime.fromisoformat(extracted_data["final_delivery_date"].replace('Z', '+00:00'))
        
    return confirm_delivery(db, po_id, extracted_data)

def recalculate_delivery_impact(db: Session, po_id: uuid.UUID, confirmed_qty: float, final_date: datetime):
    # This traces back PO -> RFQ -> SalesOrder to compare required date vs final_date
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po or not po.rfq_id:
        return
        
    rfq_item = db.query(RFQItem).filter(RFQItem.rfq_id == po.rfq_id).first()
    if not rfq_item:
        return
        
    ordered_qty = rfq_item.quantity
    
    # In a full app, we'd explicitly link RFQ -> PR -> SalesOrder. For this prototype, we'll
    # query for any SalesOrder that might be open and grab its required_date.
    so = db.query(SalesOrder).filter(SalesOrder.status == "Confirmed").first()
    if not so or not so.required_date:
        return
        
    required_date = datetime.fromisoformat(so.required_date.replace('Z', '+00:00'))
    
    # Naive timezone handling for prototype
    if required_date.tzinfo is None:
        required_date = required_date.replace(tzinfo=timezone.utc)
    if final_date.tzinfo is None:
        final_date = final_date.replace(tzinfo=timezone.utc)
        
    delay_days = (final_date - required_date).days
    shortfall = ordered_qty - confirmed_qty
    shortfall_pct = shortfall / ordered_qty if ordered_qty > 0 else 0
    
    severity = None
    if shortfall_pct > 0.20 or delay_days > 7:
        severity = "HIGH"
    elif shortfall_pct > 0.10 or delay_days > 3:
        severity = "MEDIUM"
    elif shortfall > 0 or delay_days > 0:
        severity = "LOW"
        
    if severity:
        risk = RiskEvent(
            supplier_id=po.supplier_id,
            purchase_order_id=po.id,
            description=f"Purchase Order Risk: Shortfall of {shortfall} units, delayed by {delay_days} days compared to Sales Order requirement.",
            severity=severity
        )
        db.add(risk)

def get_po_risks(db: Session, po_id: uuid.UUID) -> list[RiskEvent]:
    return db.query(RiskEvent).filter(RiskEvent.purchase_order_id == po_id).all()
