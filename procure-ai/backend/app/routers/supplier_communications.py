from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
from app.db.session import get_db
from app.models.advanced import SupplierCommunication
from app.models.procurement import SupplierQuote, SupplierQuoteItem, RFQItem, RFQ
from app.services.ai_extraction import extract_quote_from_email

router = APIRouter(prefix="/supplier-communications", tags=["communications"])

class MockInbound(BaseModel):
    rfq_id: uuid.UUID
    supplier_id: uuid.UUID
    raw_text: str

@router.post("/mock-inbound")
def create_mock_inbound(data: MockInbound, db: Session = Depends(get_db)):
    """Simulates an inbound email from a supplier."""
    comm = SupplierCommunication(
        supplier_id=data.supplier_id,
        message=data.raw_text,
        direction="inbound"
    )
    db.add(comm)
    db.commit()
    db.refresh(comm)
    return {"status": "ok", "comm_id": comm.id, "rfq_id": data.rfq_id}

@router.post("/{comm_id}/extract")
def extract_quote(comm_id: uuid.UUID, rfq_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Extracts quote details from an inbound communication using AI and saves it.
    Requires rfq_id to know which RFQ this email belongs to (in a real system, 
    this might be parsed from the email subject/thread).
    """
    comm = db.query(SupplierCommunication).filter(SupplierCommunication.id == comm_id).first()
    if not comm:
        raise HTTPException(status_code=404, detail="Communication not found")
        
    if comm.direction != "inbound":
        raise HTTPException(status_code=400, detail="Can only extract from inbound communications")
        
    # Get the pending quote placeholder for this supplier and RFQ
    quote = db.query(SupplierQuote).filter(
        SupplierQuote.rfq_id == rfq_id,
        SupplierQuote.supplier_id == comm.supplier_id
    ).first()
    
    if not quote:
        raise HTTPException(status_code=404, detail="No matching SupplierQuote found for this RFQ and Supplier")

    # Fetch context: what did we ask for?
    rfq_items = db.query(RFQItem).filter(RFQItem.rfq_id == rfq_id).all()
    context = [{"material_id": str(i.material_id), "quantity": i.quantity} for i in rfq_items]
    
    # Run AI extraction
    extracted = extract_quote_from_email(comm.message, {"requested_items": context})
    
    # Update Quote header
    quote.status = "Extracted"
    if extracted.delivery_date:
        quote.delivery_date = extracted.delivery_date
    if extracted.validity_days:
        quote.validity_days = extracted.validity_days
    if extracted.payment_terms:
        quote.payment_terms = extracted.payment_terms
        
    # For simplicity, assume 1 item per RFQ in this PoC to map the quote item
    # In a robust system, you'd match by material name/part number
    if rfq_items:
        first_item = rfq_items[0]
        # Check if SupplierQuoteItem exists, else create
        sq_item = db.query(SupplierQuoteItem).filter(
            SupplierQuoteItem.quote_id == quote.id,
            SupplierQuoteItem.rfq_item_id == first_item.id
        ).first()
        
        if not sq_item:
            sq_item = SupplierQuoteItem(quote_id=quote.id, rfq_item_id=first_item.id)
            db.add(sq_item)
            
        sq_item.unit_price = extracted.unit_price
        sq_item.quoted_quantity = extracted.quoted_quantity
        sq_item.moq = extracted.moq
        sq_item.lead_time_days = extracted.lead_time_days
        sq_item.manufacturer_part_number = extracted.manufacturer_part_number

    db.commit()
    db.refresh(quote)
    
    return {"status": "success", "quote_id": quote.id, "extracted_data": extracted.model_dump()}
