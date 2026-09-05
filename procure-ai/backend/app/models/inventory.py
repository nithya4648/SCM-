from sqlalchemy import ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.db.base import BaseModel

class Inventory(BaseModel):
    __tablename__ = "inventory"
    
    material_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    quantity_on_hand: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Relationships
    material: Mapped["Material"] = relationship(back_populates="inventory")
