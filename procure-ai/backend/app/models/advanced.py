from typing import Optional
from sqlalchemy import String, Text, ForeignKey, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from datetime import datetime

from app.db.base import BaseModel

class SupplierCommunication(BaseModel):
    __tablename__ = "supplier_communications"
    
    supplier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    direction: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., "inbound", "outbound"
    
    # Relationships
    supplier: Mapped["Supplier"] = relationship(back_populates="communications")


class DeliveryCommitment(BaseModel):
    __tablename__ = "delivery_commitments"
    
    purchase_order_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("purchase_order_items.id", ondelete="CASCADE"), nullable=False)
    committed_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    purchase_order_item: Mapped["PurchaseOrderItem"] = relationship(back_populates="delivery_commitments")


class ProcurementRecommendation(BaseModel):
    __tablename__ = "procurement_recommendations"
    
    material_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    rfq_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("rfqs.id", ondelete="SET NULL"), nullable=True)
    supplier_quote_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("supplier_quotes.id", ondelete="SET NULL"), nullable=True)
    recommended_action: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    material: Mapped["Material"] = relationship(back_populates="procurement_recommendations")
    supplier_quote: Mapped[Optional["SupplierQuote"]] = relationship()


class RiskEvent(BaseModel):
    __tablename__ = "risk_events"
    
    supplier_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("suppliers.id", ondelete="CASCADE"))
    purchase_order_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., "low", "medium", "high"
    
    # Relationships
    supplier: Mapped[Optional["Supplier"]] = relationship(back_populates="risk_events")
    purchase_order: Mapped[Optional["PurchaseOrder"]] = relationship()
