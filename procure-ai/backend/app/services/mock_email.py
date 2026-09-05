from sqlalchemy.orm import Session
from app.models.advanced import SupplierCommunication
import uuid

def dispatch_rfq_email(db: Session, supplier_id: uuid.UUID, rfq_id: uuid.UUID, material_name: str, quantity: float, required_date: str):
    """
    Mock email dispatch. Instead of sending an actual email, it creates a 
    SupplierCommunication record tracking the outbound RFQ message.
    """
    message = (
        f"Dear Supplier,\n\n"
        f"We are requesting a quote for the following material:\n"
        f"Material: {material_name}\n"
        f"Quantity: {quantity}\n"
        f"Required Delivery Date: {required_date}\n\n"
        f"Please reference RFQ ID: {rfq_id} in your response.\n"
        f"Thank you."
    )
    
    communication = SupplierCommunication(
        supplier_id=supplier_id,
        message=message,
        direction="outbound"
    )
    
    db.add(communication)
    db.commit()
    db.refresh(communication)
    return communication
