import uuid
from abc import ABC, abstractmethod

class ERPAdapter(ABC):
    @abstractmethod
    def push_po(self, po_id: uuid.UUID) -> str:
        """
        Pushes the given Purchase Order ID to the external ERP system.
        Returns the ERP-specific reference ID.
        """
        pass

class MockERPAdapter(ERPAdapter):
    def push_po(self, po_id: uuid.UUID) -> str:
        """
        Mocks the ERP push process and returns a fake ERP transaction ID.
        In a real scenario, this would format the PO payload and call an SAP/Oracle API.
        """
        # Simulate an ERP response
        return f"ERP-MOCK-{uuid.uuid4().hex[:8].upper()}"

# We can dependency-inject this later or just instantiate the mock directly for now
def get_erp_adapter() -> ERPAdapter:
    return MockERPAdapter()
