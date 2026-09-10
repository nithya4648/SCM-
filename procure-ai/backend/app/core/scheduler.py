import logging
# pyrefly: ignore [missing-import]
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from app.db.session import SessionLocal
from app.routers.shortages import compute_shortages
from app.services.rfq_service import create_rfq
from app.schemas.rfq import RFQCreate
from app.models.procurement import RFQ, RFQItem
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def check_shortages_and_create_rfqs():
    db: Session = SessionLocal()
    try:
        shortages = compute_shortages(db)
        for shortage in shortages:
            if shortage["shortage_quantity"] > 0:
                # Check if an RFQItem for this material_id exists on an "Open" RFQ
                existing_rfq_item = db.query(RFQItem).join(RFQ).filter(
                    RFQItem.material_id == shortage["material_id"],
                    RFQ.status == "Open"
                ).first()
                
                if existing_rfq_item:
                    continue
                
                # Create RFQ
                # TODO: This should trace back to the sales order required_date
                required_date = (datetime.utcnow() + timedelta(days=14)).strftime("%Y-%m-%d")
                
                rfq_data = RFQCreate(
                    quantity=shortage["shortage_quantity"],
                    required_date=required_date
                )
                
                try:
                    create_rfq(db=db, material_id=shortage["material_id"], data=rfq_data)
                    logger.info(f"Auto-created RFQ for material {shortage['material_id']} with quantity {shortage['shortage_quantity']}")
                except Exception as e:
                    logger.error(f"Failed to auto-create RFQ for material {shortage['material_id']}: {e}")
                    
    except Exception as e:
        logger.error(f"Error in check_shortages_and_create_rfqs loop: {e}")
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_shortages_and_create_rfqs, 'interval', minutes=5)
    scheduler.start()
    logger.info("Scheduler started.")
