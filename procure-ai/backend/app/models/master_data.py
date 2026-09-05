from typing import List, Optional
from sqlalchemy import String, Text, ForeignKey, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.db.base import BaseModel

class Customer(BaseModel):
    __tablename__ = "customers"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    
    # Relationships
    sales_orders: Mapped[List["SalesOrder"]] = relationship(back_populates="customer", cascade="all, delete-orphan")


class Product(BaseModel):
    __tablename__ = "products"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    bom_headers: Mapped[List["BOMHeader"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    sales_order_items: Mapped[List["SalesOrderItem"]] = relationship(back_populates="product", cascade="all, delete-orphan")


class Material(BaseModel):
    __tablename__ = "materials"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    bom_items: Mapped[List["BOMItem"]] = relationship(back_populates="material", cascade="all, delete-orphan")
    inventory: Mapped[List["Inventory"]] = relationship(back_populates="material", cascade="all, delete-orphan")
    supplier_materials: Mapped[List["SupplierMaterial"]] = relationship(back_populates="material", cascade="all, delete-orphan")
    purchase_requisitions: Mapped[List["PurchaseRequisition"]] = relationship(back_populates="material", cascade="all, delete-orphan")
    rfq_items: Mapped[List["RFQItem"]] = relationship(back_populates="material", cascade="all, delete-orphan")
    purchase_order_items: Mapped[List["PurchaseOrderItem"]] = relationship(back_populates="material", cascade="all, delete-orphan")
    procurement_recommendations: Mapped[List["ProcurementRecommendation"]] = relationship(back_populates="material", cascade="all, delete-orphan")


class BOMHeader(BaseModel):
    __tablename__ = "bom_headers"
    
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Relationships
    product: Mapped["Product"] = relationship(back_populates="bom_headers")
    items: Mapped[List["BOMItem"]] = relationship(back_populates="header", cascade="all, delete-orphan")


class BOMItem(BaseModel):
    __tablename__ = "bom_items"
    
    bom_header_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bom_headers.id", ondelete="CASCADE"), nullable=False)
    material_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    header: Mapped["BOMHeader"] = relationship(back_populates="items")
    material: Mapped["Material"] = relationship(back_populates="bom_items")
