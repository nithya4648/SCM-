from sqlalchemy.orm import Session
from fastapi import HTTPException
import uuid
from app.models.procurement import RFQ, RFQItem, SupplierQuote
from app.models.master_data import Material
from app.models.suppliers import SupplierMaterial, Supplier
from app.schemas.rfq import RFQCreate
from app.services.mock_email import dispatch_rfq_email

def create_rfq(db: Session, material_id: uuid.UUID, data: RFQCreate) -> RFQ:
    # 1. Validate material exists
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
        
    supplier_ids = []
    
    # 2. Determine suppliers
    if data.supplier_id:
        # Controlled non-standard sourcing fallback
        supplier = db.query(Supplier).filter(Supplier.id == data.supplier_id).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Explicit supplier_id not found")
        supplier_ids.append(supplier.id)
        # Note: You could log this flag in a separate audit log or as a field on RFQ.
    else:
        # Lookup approved suppliers for this material
        approved_mappings = db.query(SupplierMaterial).filter(SupplierMaterial.material_id == material_id).all()
        if not approved_mappings:
            raise HTTPException(status_code=400, detail="No approved suppliers found for this material. Provide supplier_id for manual sourcing.")
        supplier_ids = [mapping.supplier_id for mapping in approved_mappings]
        
    # 3. Create RFQ
    new_rfq = RFQ(status="Open")
    db.add(new_rfq)
    db.flush() # get new_rfq.id
    
    # 4. Create RFQ Item
    rfq_item = RFQItem(
        rfq_id=new_rfq.id,
        material_id=material_id,
        quantity=data.quantity
    )
    db.add(rfq_item)
    db.flush()
    
    # 5. Create SupplierQuotes (acting as the placeholder for their response) and dispatch emails
    for sup_id in supplier_ids:
        quote_placeholder = SupplierQuote(
            rfq_id=new_rfq.id,
            supplier_id=sup_id,
            status="Pending"
        )
        db.add(quote_placeholder)
        
        # Dispatch mock email
        dispatch_rfq_email(
            db=db, 
            supplier_id=sup_id, 
            rfq_id=new_rfq.id, 
            material_name=material.name, 
            quantity=data.quantity, 
            required_date=data.required_date
        )
        
    db.commit()
    db.refresh(new_rfq)
    return new_rfq


def get_rfq(db: Session, rfq_id: uuid.UUID) -> RFQ:
    rfq = db.query(RFQ).filter(RFQ.id == rfq_id).first()
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    return rfq
