from sqlalchemy.orm import Session
import uuid
from fastapi import HTTPException
from app.models.procurement import PurchaseOrder, PurchaseOrderItem, SupplierQuote, SupplierQuoteItem
from app.models.advanced import ProcurementRecommendation
from app.services.erp_adapter import get_erp_adapter

def approve_recommendation(db: Session, recommendation_id: uuid.UUID) -> PurchaseOrder:
    """
    Takes an approved recommendation, finds the underlying supplier quote,
    generates a Purchase Order, pushes it to the ERP via adapter, and saves.
    """
    rec = db.query(ProcurementRecommendation).filter(ProcurementRecommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    if not rec.supplier_quote_id:
        raise HTTPException(status_code=400, detail="Recommendation does not have a linked supplier quote")
        
    quote = db.query(SupplierQuote).filter(SupplierQuote.id == rec.supplier_quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Linked supplier quote not found")
        
    # Create the PO
    po = PurchaseOrder(
        supplier_id=quote.supplier_id,
        rfq_id=rec.rfq_id,
        status="Created"
    )
    db.add(po)
    db.flush() # flush to get PO ID
    
    # Create PO items from Quote items
    quote_items = db.query(SupplierQuoteItem).filter(SupplierQuoteItem.quote_id == quote.id).all()
    for qi in quote_items:
        # Get material id from rfq item
        po_item = PurchaseOrderItem(
            purchase_order_id=po.id,
            material_id=qi.rfq_item.material_id,
            quantity=qi.quoted_quantity if qi.quoted_quantity else qi.rfq_item.quantity,
            unit_price=qi.unit_price if qi.unit_price else 0.0
        )
        db.add(po_item)
    
    # Push to ERP
    erp_adapter = get_erp_adapter()
    erp_ref = erp_adapter.push_po(po.id)
    po.erp_reference = erp_ref
    
    # Update recommendation action
    rec.recommended_action = "approved_and_po_created"
    
    db.commit()
    db.refresh(po)
    return po

def get_po(db: Session, po_id: uuid.UUID) -> PurchaseOrder:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    return po
