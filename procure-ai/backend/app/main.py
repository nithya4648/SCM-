from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.routers.rfq import router as procurement_router, rfq_router
from app.routers.supplier_communications import router as comms_router
from app.routers.po import rec_router, po_router
from app.routers.delivery import router as delivery_router
from app.routers.dashboard import router as dashboard_router
from app.routers.shortages import router as shortages_router

from contextlib import asynccontextmanager
from app.core.scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield

app = FastAPI(title="Procure AI API", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(procurement_router)
app.include_router(rfq_router)
app.include_router(comms_router)
app.include_router(rec_router)
app.include_router(po_router)
app.include_router(delivery_router)
app.include_router(dashboard_router)
app.include_router(shortages_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).scalar()
        return {"status": "ok", "db_result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
