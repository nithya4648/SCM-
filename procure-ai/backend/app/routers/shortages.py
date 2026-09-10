from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
import uuid
from typing import List

from app.db.session import get_db
from app.models.master_data import Material, BOMItem
from app.models.inventory import Inventory
from app.models.sales import SalesOrderItem

router = APIRouter(prefix="/shortages", tags=["shortages"])

class ShortageResponse(BaseModel):
    material_id: uuid.UUID
    material_name: str
    required_quantity: float
    inventory_quantity: float
    open_po_quantity: float
    shortage_quantity: float

    class Config:
        from_attributes = True

def compute_shortages(db: Session):
    from app.models.procurement import PurchaseOrder, PurchaseOrderItem
    sales_items = db.query(SalesOrderItem).all()
    
    required_mats = {}
    for item in sales_items:
        bom_items = db.query(BOMItem).join(BOMItem.header).filter(BOMItem.header.has(product_id=item.product_id)).all()
        for b_item in bom_items:
            req_qty = b_item.quantity * item.quantity
            required_mats[b_item.material_id] = required_mats.get(b_item.material_id, 0) + req_qty
            
    shortages = []
    for mat_id, req_qty in required_mats.items():
        inv = db.query(Inventory).filter(Inventory.material_id == mat_id).first()
        inv_qty = inv.quantity_on_hand if inv else 0
        
        po_sum = db.query(func.sum(PurchaseOrderItem.quantity)).join(PurchaseOrder).filter(
            PurchaseOrderItem.material_id == mat_id,
            PurchaseOrder.status.in_(("Created", "Confirmed"))
        ).scalar()
        open_po_qty = float(po_sum) if po_sum else 0.0

        total_supply = inv_qty + open_po_qty
        
        if total_supply < req_qty:
            mat = db.query(Material).filter(Material.id == mat_id).first()
            shortages.append({
                "material_id": mat_id,
                "material_name": mat.name if mat else "Unknown",
                "required_quantity": req_qty,
                "inventory_quantity": inv_qty,
                "open_po_quantity": open_po_qty,
                "shortage_quantity": req_qty - total_supply
            })
            
    return shortages

@router.get("/", response_model=List[ShortageResponse])
def get_shortages_endpoint(db: Session = Depends(get_db)):
    """
    Computes material shortages by comparing BOM requirements against inventory.
    """
    return compute_shortages(db)
