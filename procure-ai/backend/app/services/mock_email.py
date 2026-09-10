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

import random

def generate_supplier_reply(material_name: str, qty: float, base_price: float, base_lead_days: int) -> str:
    """
    Generates a synthetic supplier reply email with varied templates and randomized pricing/lead time.
    """
    price_var = base_price * random.uniform(0.85, 1.15)
    lead_var = max(1, base_lead_days + random.randint(-5, 5))
    
    include_moq = random.choice([True, False])
    moq = int(qty * random.uniform(0.5, 1.5)) if include_moq else None
    
    templates = [
        "Hello,\n\nWe can supply {material_name}.\nPrice: ${price:.2f}/unit\nLead time: {lead_days} days.{moq_text}\n\nThanks.",
        "Hi there, regarding your RFQ for {qty} of {material_name}:\nOur unit price is ${price:.2f}. We estimate delivery in {lead_days} days.{moq_text}\nBest regards.",
        "Quote for {material_name}:\n- Unit cost: ${price:.2f}\n- Delivery: {lead_days} days{moq_text}\nLet us know if you want to proceed.",
        "Dear customer,\nThank you for reaching out. For {material_name}, we offer a price of ${price:.2f} per unit. It will take around {lead_days} days to ship.{moq_text}"
    ]
    
    moq_text = f"\nMOQ: {moq}" if include_moq else ""
    
    template = random.choice(templates)
    return template.format(
        material_name=material_name,
        qty=qty,
        price=price_var,
        lead_days=lead_var,
        moq_text=moq_text
    )
