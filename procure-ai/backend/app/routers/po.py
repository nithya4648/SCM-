from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from app.db.session import get_db
from app.schemas.po import POResponse, PODetailResponse
from app.services import po_service

rec_router = APIRouter(prefix="/recommendations", tags=["recommendations"])
po_router = APIRouter(prefix="/purchase-orders", tags=["purchase_orders"])

@rec_router.post("/{recommendation_id}/approve", response_model=POResponse)
def approve_recommendation_endpoint(recommendation_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Approve a procurement recommendation.
    Generates a PO from the winning supplier quote and pushes it to the ERP.
    """
    return po_service.approve_recommendation(db, recommendation_id)

@po_router.get("/{po_id}", response_model=PODetailResponse)
def get_po_endpoint(po_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve a Purchase Order by ID.
    """
    return po_service.get_po(db, po_id)
