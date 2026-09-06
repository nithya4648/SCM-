from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from typing import List

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
    try:
        return po_service.approve_recommendation(db, recommendation_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@po_router.get("/", response_model=List[PODetailResponse])
def list_pos_endpoint(db: Session = Depends(get_db)):
    """
    List all Purchase Orders.
    """
    try:
        return po_service.list_pos(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@po_router.get("/{po_id}", response_model=PODetailResponse)
def get_po_endpoint(po_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve a Purchase Order by ID.
    """
    try:
        return po_service.get_po(db, po_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

