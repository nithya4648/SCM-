from typing import List, Optional
from sqlalchemy import String, ForeignKey, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.db.base import BaseModel

class Supplier(BaseModel):
    __tablename__ = "suppliers"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    reliability_score: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Relationships
    supplier_materials: Mapped[List["SupplierMaterial"]] = relationship(back_populates="supplier", cascade="all, delete-orphan")
    supplier_quotes: Mapped[List["SupplierQuote"]] = relationship(back_populates="supplier", cascade="all, delete-orphan")
    purchase_orders: Mapped[List["PurchaseOrder"]] = relationship(back_populates="supplier", cascade="all, delete-orphan")
    communications: Mapped[List["SupplierCommunication"]] = relationship(back_populates="supplier", cascade="all, delete-orphan")
    risk_events: Mapped[List["RiskEvent"]] = relationship(back_populates="supplier", cascade="all, delete-orphan")


class SupplierMaterial(BaseModel):
    __tablename__ = "supplier_materials"
    
    supplier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    material_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    supplier: Mapped["Supplier"] = relationship(back_populates="supplier_materials")
    material: Mapped["Material"] = relationship(back_populates="supplier_materials")
