from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.db.session import get_db
from app.schemas.rfq import RFQCreate, RFQResponse
from app.schemas.recommendation import ComparisonResponse
from app.services import rfq_service, recommendation_engine, ai_extraction

router = APIRouter(prefix="/procurement", tags=["procurement"])
rfq_router = APIRouter(prefix="/rfqs", tags=["rfq"])

@router.post("/{material_id}/rfq", response_model=RFQResponse)
def create_rfq_endpoint(material_id: uuid.UUID, rfq_in: RFQCreate, db: Session = Depends(get_db)):
    """
    Create a new RFQ for a given material.
    Will dispatch mock emails to approved suppliers or to a specified fallback supplier.
    """
    return rfq_service.create_rfq(db, material_id, rfq_in)

@rfq_router.get("/{rfq_id}", response_model=RFQResponse)
def get_rfq_endpoint(rfq_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve an RFQ by ID along with its items and supplier quotes.
    """
    return rfq_service.get_rfq(db, rfq_id)

@rfq_router.post("/{rfq_id}/compare", response_model=ComparisonResponse)
def compare_rfq_endpoint(rfq_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Compare supplier quotes for the given RFQ using deterministic scoring and generate
    a natural‑language explanation via LLM.
    Stores the recommendation in the ProcurementRecommendation table.
    """
    try:
        comparison = recommendation_engine.compare_quotes(rfq_id, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    explanation = ai_extraction.generate_recommendation_explanation(comparison)

    from app.models.advanced import ProcurementRecommendation
    from app.models.procurement import RFQItem
    rfq_item = db.query(RFQItem).filter(RFQItem.rfq_id == rfq_id).first()
    if rfq_item:
        best_quote_id = comparison["best_match"]["quote_id"] if comparison.get("best_match") else None
        rec = ProcurementRecommendation(
            material_id=rfq_item.material_id,
            rfq_id=rfq_id,
            supplier_quote_id=best_quote_id,
            recommended_action="select_supplier",
            reason=explanation,
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        comparison["recommendation_id"] = str(rec.id)
    comparison["explanation"] = explanation
    return comparison

# Note: rfq_router is included in the main application elsewhere.
