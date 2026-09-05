from typing import List, Optional
from sqlalchemy import String, ForeignKey, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.db.base import BaseModel

class PurchaseRequisition(BaseModel):
    __tablename__ = "purchase_requisitions"
    
    status: Mapped[str] = mapped_column(String(50), default="Pending")
    material_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    requested_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    material: Mapped["Material"] = relationship(back_populates="purchase_requisitions")


class RFQ(BaseModel):
    __tablename__ = "rfqs"
    
    status: Mapped[str] = mapped_column(String(50), default="Open")
    
    # Relationships
    items: Mapped[List["RFQItem"]] = relationship(back_populates="rfq", cascade="all, delete-orphan")
    quotes: Mapped[List["SupplierQuote"]] = relationship(back_populates="rfq", cascade="all, delete-orphan")


class RFQItem(BaseModel):
    __tablename__ = "rfq_items"
    
    rfq_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False)
    material_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    rfq: Mapped["RFQ"] = relationship(back_populates="items")
    material: Mapped["Material"] = relationship(back_populates="rfq_items")
    quote_items: Mapped[List["SupplierQuoteItem"]] = relationship(back_populates="rfq_item", cascade="all, delete-orphan")


class SupplierQuote(BaseModel):
    __tablename__ = "supplier_quotes"
    
    rfq_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False)
    supplier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="Submitted")
    delivery_date: Mapped[str] = mapped_column(String(100), nullable=True)
    validity_days: Mapped[int] = mapped_column(Integer, nullable=True)
    payment_terms: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Relationships
    rfq: Mapped["RFQ"] = relationship(back_populates="quotes")
    supplier: Mapped["Supplier"] = relationship(back_populates="supplier_quotes")
    items: Mapped[List["SupplierQuoteItem"]] = relationship(back_populates="quote", cascade="all, delete-orphan")


class SupplierQuoteItem(BaseModel):
    __tablename__ = "supplier_quote_items"
    
    quote_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("supplier_quotes.id", ondelete="CASCADE"), nullable=False)
    rfq_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rfq_items.id", ondelete="CASCADE"), nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=True)
    quoted_quantity: Mapped[float] = mapped_column(Float, nullable=True)
    moq: Mapped[float] = mapped_column(Float, nullable=True)
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=True)
    manufacturer_part_number: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Relationships
    quote: Mapped["SupplierQuote"] = relationship(back_populates="items")
    rfq_item: Mapped["RFQItem"] = relationship(back_populates="quote_items")


class PurchaseOrder(BaseModel):
    __tablename__ = "purchase_orders"
    
    supplier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    rfq_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("rfqs.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Created")
    erp_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    supplier: Mapped["Supplier"] = relationship(back_populates="purchase_orders")
    rfq: Mapped[Optional["RFQ"]] = relationship()
    items: Mapped[List["PurchaseOrderItem"]] = relationship(back_populates="purchase_order", cascade="all, delete-orphan")


class PurchaseOrderItem(BaseModel):
    __tablename__ = "purchase_order_items"
    
    purchase_order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False)
    material_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    purchase_order: Mapped["PurchaseOrder"] = relationship(back_populates="items")
    material: Mapped["Material"] = relationship(back_populates="purchase_order_items")
    delivery_commitments: Mapped[List["DeliveryCommitment"]] = relationship(back_populates="purchase_order_item", cascade="all, delete-orphan")
