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
    shortage_quantity: float

    class Config:
        from_attributes = True

@router.get("/", response_model=List[ShortageResponse])
def get_shortages_endpoint(db: Session = Depends(get_db)):
    """
    Computes material shortages by comparing BOM requirements against inventory.
    """
    # Very simplified shortage detection:
    # 1. Sum up all required quantities from all SalesOrderItems via BOM
    # 2. Subtract inventory on hand
    
    # Get all active sales order items
    sales_items = db.query(SalesOrderItem).all()
    
    required_mats = {}
    for item in sales_items:
        # Find BOM for product
        # For simplicity, assuming product.bom_headers has 1 header
        bom_items = db.query(BOMItem).join(BOMItem.header).filter(BOMItem.header.has(product_id=item.product_id)).all()
        for b_item in bom_items:
            req_qty = b_item.quantity * item.quantity
            required_mats[b_item.material_id] = required_mats.get(b_item.material_id, 0) + req_qty
            
    shortages = []
    for mat_id, req_qty in required_mats.items():
        inv = db.query(Inventory).filter(Inventory.material_id == mat_id).first()
        inv_qty = inv.quantity_on_hand if inv else 0
        
        if inv_qty < req_qty:
            mat = db.query(Material).filter(Material.id == mat_id).first()
            shortages.append({
                "material_id": mat_id,
                "material_name": mat.name if mat else "Unknown",
                "required_quantity": req_qty,
                "inventory_quantity": inv_qty,
                "shortage_quantity": req_qty - inv_qty
            })
            
    return shortages
