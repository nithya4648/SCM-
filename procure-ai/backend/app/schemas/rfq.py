from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

class RFQCreate(BaseModel):
    quantity: float = Field(..., gt=0, description="Quantity of material requested")
    required_date: str = Field(..., description="Required delivery date (ISO format string)")
    supplier_id: Optional[uuid.UUID] = Field(None, description="Optional: specific supplier to ask (bypasses approved supplier list)")

class RFQItemResponse(BaseModel):
    id: uuid.UUID
    rfq_id: uuid.UUID
    material_id: uuid.UUID
    quantity: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SupplierQuoteItemResponse(BaseModel):
    id: Optional[uuid.UUID] = None
    rfq_item_id: Optional[uuid.UUID] = None
    unit_price: Optional[float] = None
    moq: Optional[float] = None
    lead_time_days: Optional[int] = None
    quoted_quantity: Optional[float] = None
    manufacturer_part_number: Optional[str] = None

    class Config:
        from_attributes = True

class SupplierQuoteResponse(BaseModel):
    id: uuid.UUID
    supplier_id: uuid.UUID
    status: str
    created_at: datetime
    items: List[SupplierQuoteItemResponse] = []

    class Config:
        from_attributes = True

class RFQResponse(BaseModel):
    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    items: List[RFQItemResponse]
    quotes: List[SupplierQuoteResponse]

    class Config:
        from_attributes = True
