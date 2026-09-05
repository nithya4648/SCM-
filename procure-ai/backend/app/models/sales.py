from typing import List, Optional
from sqlalchemy import String, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.db.base import BaseModel

class SalesOrder(BaseModel):
    __tablename__ = "sales_orders"
    
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="Pending")
    required_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="sales_orders")
    items: Mapped[List["SalesOrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class SalesOrderItem(BaseModel):
    __tablename__ = "sales_order_items"
    
    sales_order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sales_orders.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    order: Mapped["SalesOrder"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="sales_order_items")
