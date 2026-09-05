from app.db.base import Base, BaseModel
from app.models.master_data import Customer, Product, Material, BOMHeader, BOMItem
from app.models.sales import SalesOrder, SalesOrderItem
from app.models.inventory import Inventory
from app.models.suppliers import Supplier, SupplierMaterial
from app.models.procurement import (
    PurchaseRequisition,
    RFQ,
    RFQItem,
    SupplierQuote,
    SupplierQuoteItem,
    PurchaseOrder,
    PurchaseOrderItem,
)
from app.models.advanced import (
    SupplierCommunication,
    DeliveryCommitment,
    ProcurementRecommendation,
    RiskEvent,
)

# This __init__.py ensures all models are imported and registered with SQLAlchemy's declarative base
__all__ = [
    "Base",
    "BaseModel",
    "Customer",
    "Product",
    "Material",
    "BOMHeader",
    "BOMItem",
    "SalesOrder",
    "SalesOrderItem",
    "Inventory",
    "Supplier",
    "SupplierMaterial",
    "PurchaseRequisition",
    "RFQ",
    "RFQItem",
    "SupplierQuote",
    "SupplierQuoteItem",
    "PurchaseOrder",
    "PurchaseOrderItem",
    "SupplierCommunication",
    "DeliveryCommitment",
    "ProcurementRecommendation",
    "RiskEvent",
]
