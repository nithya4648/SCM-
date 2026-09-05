from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid
from typing import List

from app.db.session import get_db
from app.schemas.delivery import (
    DeliveryConfirmRequest,
    DeliveryEmailRequest,
    RiskEventResponse,
    DeliveryCommitmentResponse
)
from app.services import delivery_service

router = APIRouter(prefix="/purchase-orders", tags=["delivery"])

@router.post("/{po_id}/confirm", response_model=DeliveryCommitmentResponse)
def confirm_delivery_endpoint(po_id: uuid.UUID, data: DeliveryConfirmRequest, db: Session = Depends(get_db)):
    """
    Simulates a supplier confirming a purchase order, partially or fully.
    """
    return delivery_service.confirm_delivery(db, po_id, data.model_dump())

@router.post("/{po_id}/confirm-from-email", response_model=DeliveryCommitmentResponse)
def confirm_delivery_from_email_endpoint(po_id: uuid.UUID, data: DeliveryEmailRequest, db: Session = Depends(get_db)):
    """
    Extracts delivery confirmation details from a messy supplier email and confirms the PO.
    """
    return delivery_service.confirm_delivery_from_email(db, po_id, data.raw_text)

@router.get("/{po_id}/risk", response_model=List[RiskEventResponse])
def get_po_risk_endpoint(po_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Returns current risk events for a given PO.
    """
    return delivery_service.get_po_risks(db, po_id)
