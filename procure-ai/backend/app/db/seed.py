import uuid
from datetime import datetime, timedelta, timezone
from app.db.session import SessionLocal
from app.models.master_data import Customer, Product, Material, BOMHeader, BOMItem
from app.models.suppliers import Supplier, SupplierMaterial
from app.models.inventory import Inventory
from app.models.sales import SalesOrder, SalesOrderItem

def seed_db():
    db = SessionLocal()
    try:
        # Customers
        c1 = Customer(name="Acme Corp", email="contact@acme.example.com")
        c2 = Customer(name="Globex", email="info@globex.example.com")
        db.add_all([c1, c2])
        
        # Products
        p1 = Product(name="Widget Pro", description="High end widget")
        p2 = Product(name="Widget Basic", description="Standard widget")
        p3 = Product(name="Super Gadget", description="Next gen gadget")
        db.add_all([p1, p2, p3])
        
        # Materials
        m1 = Material(name="Steel Sheet", description="2mm steel")
        m2 = Material(name="Aluminum Frame", description="Standard frame")
        m3 = Material(name="Circuit Board v1", description="Main logic board")
        m4 = Material(name="Rubber Screws", description="Pack of 100")
        m5 = Material(name="Plastic Casing", description="Outer shell")
        db.add_all([m1, m2, m3, m4, m5])
        
        db.flush() # flush to get IDs
        
        # BOM for Product 1 (Widget Pro) using Material 1, 3, 5
        bom = BOMHeader(product_id=p1.id, quantity=1.0)
        db.add(bom)
        db.flush()
        
        bom_items = [
            BOMItem(bom_header_id=bom.id, material_id=m1.id, quantity=2.0),
            BOMItem(bom_header_id=bom.id, material_id=m3.id, quantity=1.0),
            BOMItem(bom_header_id=bom.id, material_id=m5.id, quantity=1.0),
        ]
        db.add_all(bom_items)
        
        # Suppliers
        s1 = Supplier(name="MetalWorks Inc", contact_email="sales@metalworks.com", reliability_score=0.95)
        s2 = Supplier(name="ElectroParts", contact_email="orders@electroparts.com", reliability_score=0.85)
        s3 = Supplier(name="PlastikCo", contact_email="supply@plastikco.com", reliability_score=0.99)
        db.add_all([s1, s2, s3])
        db.flush()
        
        # Supplier Materials mappings
        sm1 = SupplierMaterial(supplier_id=s1.id, material_id=m1.id, lead_time_days=14, price=10.50)
        sm2 = SupplierMaterial(supplier_id=s1.id, material_id=m2.id, lead_time_days=10, price=15.00)
        sm3 = SupplierMaterial(supplier_id=s2.id, material_id=m3.id, lead_time_days=30, price=45.00)
        sm4 = SupplierMaterial(supplier_id=s3.id, material_id=m5.id, lead_time_days=7, price=5.25)
        db.add_all([sm1, sm2, sm3, sm4])
        
        # Inventory (intentionally low on m2 to create a shortage)
        inv1 = Inventory(material_id=m1.id, quantity_on_hand=500)
        inv2 = Inventory(material_id=m3.id, quantity_on_hand=150)
        inv3 = Inventory(material_id=m5.id, quantity_on_hand=1000)
        # m2 and m4 have zero inventory (no rows) — these are shortage candidates
        db.add_all([inv1, inv2, inv3])
        
        # Sales Order with required_date 30 days from now
        required = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d")
        so1 = SalesOrder(customer_id=c1.id, status="Confirmed", required_date=required)
        db.add(so1)
        db.flush()
        
        # Sales Order Items — order 500 Widget Pro (needs 1000 Steel, 500 Circuit, 500 Plastic via BOM)
        soi1 = SalesOrderItem(sales_order_id=so1.id, product_id=p1.id, quantity=500, unit_price=150.00)
        db.add(soi1)
        
        db.commit()
        print("Database seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()

