from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

class DeliveryConfirmRequest(BaseModel):
    confirmed_quantity: float = Field(..., description="Quantity the supplier commits to deliver")
    first_delivery_date: datetime = Field(..., description="Date of the first delivery")
    final_delivery_date: Optional[datetime] = Field(None, description="Date of final delivery if split")

class DeliveryEmailRequest(BaseModel):
    raw_text: str = Field(..., description="Raw email text from supplier")

class RiskEventResponse(BaseModel):
    id: uuid.UUID
    supplier_id: Optional[uuid.UUID]
    purchase_order_id: Optional[uuid.UUID]
    description: str
    severity: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class DeliveryCommitmentResponse(BaseModel):
    id: uuid.UUID
    purchase_order_item_id: uuid.UUID
    committed_date: datetime
    quantity: float
    created_at: datetime
    
    class Config:
        from_attributes = True
