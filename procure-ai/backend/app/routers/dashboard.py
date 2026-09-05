from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from app.db.session import get_db
from app.models.procurement import PurchaseRequisition, RFQ
from app.models.advanced import SupplierCommunication, RiskEvent
from app.routers.shortages import get_shortages_endpoint

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

class DashboardSummaryResponse(BaseModel):
    open_procurement_requirements: int
    critical_shortages: int
    rfqs_awaiting: int
    supplier_responses: int
    pos_at_risk: int

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Returns aggregate counts for the dashboard.
    """
    open_reqs = db.query(PurchaseRequisition).filter(PurchaseRequisition.status != "Fulfilled").count()
    
    # We reuse the logic from shortages endpoint to count critical shortages
    shortages = get_shortages_endpoint(db)
    critical_shortages = len(shortages)
    
    rfqs_awaiting = db.query(RFQ).filter(RFQ.status == "Open").count()
    
    supplier_responses = db.query(SupplierCommunication).filter(SupplierCommunication.direction == "inbound").count()
    
    # Count distinct POs that have a HIGH severity risk event
    pos_at_risk = db.query(RiskEvent.purchase_order_id).filter(
        RiskEvent.severity == "HIGH", 
        RiskEvent.purchase_order_id.isnot(None)
    ).distinct().count()
    
    return DashboardSummaryResponse(
        open_procurement_requirements=open_reqs,
        critical_shortages=critical_shortages,
        rfqs_awaiting=rfqs_awaiting,
        supplier_responses=supplier_responses,
        pos_at_risk=pos_at_risk
    )
