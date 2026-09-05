from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

class POItemResponse(BaseModel):
    id: uuid.UUID
    material_id: uuid.UUID
    quantity: float
    unit_price: float

    class Config:
        from_attributes = True

class POResponse(BaseModel):
    id: uuid.UUID
    supplier_id: uuid.UUID
    rfq_id: Optional[uuid.UUID]
    status: str
    erp_reference: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[POItemResponse]

    class Config:
        from_attributes = True

# We'll use a deeper response for the detail endpoint later if needed (e.g., nesting deliveries and risks)
class PODetailResponse(POResponse):
    # This can be expanded as we add schemas for delivery commitments and risk events
    pass
