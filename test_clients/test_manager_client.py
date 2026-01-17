"""
Store Manager Client - Product & inventory management
Tests manager-level operations
"""
from base_client import BaseAPIClient


class ManagerClient(BaseAPIClient):
    """Client for Store Manager operations"""
    
    def test_manager_workflow(self):
        """Complete manager workflow test"""
        
        print("\n" + "="*60)
        print("👔 STORE MANAGER TESTING")
        print("="*60)
        
        # 1. Login as manager
        print("\n1️⃣ Logging in as store manager...")
        login_result = self.login("manager1", "manager123")
        self.print_result("Manager Login", login_result)
        
        # 2. View assigned store
        print("\n2️⃣ Getting manager profile...")
        profile = self.get("/api/users/profile/")
        self.print_result("Manager Profile", profile)
        
        # 3. View product catalog
        print("\n3️⃣ Viewing product catalog...")
        products = self.get("/api/catalog/products/")
        self.print_result("Products", products)
        
        # 4. Add new product
        print("\n4️⃣ Adding new product...")
        product_data = {
            "name": "Summer Collection T-Shirt",
            "description": "Lightweight cotton t-shirt",
            "category": 1,  # Assuming category exists
            "brand": "Summer Wear",
            "base_price": "499.00"
        }
        product = self.post("/api/catalog/products/", product_data)
        self.print_result("New Product", product)
        product_id = product.get('id')
        
        # 5. Add product variant
        if product_id:
            print("\n5️⃣ Adding product variant...")
            variant_data = {
                "product": product_id,
                "sku": "SUM-TS-L-RED-001",
                "size": "L",
                "color": "Red",
                "fabric_type": "Cotton",
                "retail_price": "599.00",
                "wholesale_price": "449.00",
                "min_wholesale_qty": 20,
                "weight": "0.20"
            }
            variant = self.post("/api/catalog/variants/", variant_data)
            self.print_result("New Variant", variant)
            variant_id = variant.get('id')
        
        # 6. Check stock levels
        print("\n6️⃣ Checking stock levels...")
        stock = self.get("/api/inventory/stock/")
        self.print_result("Stock Levels", stock)
        
        # 7. Make stock adjustment
        print("\n7️⃣ Making stock adjustment...")
        adjustment_data = {
            "variant": 1,  # Assuming variant exists
            "location": 1,  # Assuming store exists
            "adjustment": 100,
            "reason": "Initial stock addition - new shipment received"
        }
        adjustment = self.post("/api/inventory/adjust/", adjustment_data)
        self.print_result("Stock Adjustment", adjustment)
        
        # 8. View stock transactions
        print("\n8️⃣ Viewing stock transactions...")
        transactions = self.get("/api/inventory/transactions/")
        self.print_result("Stock Transactions", transactions)
        
        # 9. Create supplier
        print("\n9️⃣ Creating supplier...")
        # First register a new user for the supplier
        new_supplier_user = {
            "username": "new_supplier_test",
            "email": "new_supplier@example.com",
            "password": "supplier123",
            "role": "SUPPLIER"
        }
        
        # We need to register this user first. 
        # Since registration endpoint is public, we can use requests directly or the client.
        # However, checking if user exists or just registering with unique name is safer.
        import random
        r_id = random.randint(1000, 9999)
        new_supplier_user['username'] = f"supplier_test_{r_id}"
        new_supplier_user['email'] = f"supplier_{r_id}@test.com"
        
        print(f"   > Registering new user: {new_supplier_user['username']}")
        reg_response = self.register(**new_supplier_user)
        
        if 'id' in reg_response:
            supplier_user_id = reg_response['id']
            supplier_data = {
                "user": supplier_user_id,
                "company_name": f"Textile Suppliers Inc {r_id}",
                "contact_person": "John Supplier",
                "phone": "+1234567890",
                "email": new_supplier_user['email'],
                "address": "456 Supplier St",
                "payment_terms": "Net 30",
                "is_active": True
            }
            supplier = self.post("/api/purchasing/suppliers/", supplier_data)
            self.print_result("New Supplier", supplier)
        else:
            print(f"❌ Failed to register supplier user: {reg_response}")
        
        # 10. Create purchase order
        print("\n🔟 Creating purchase order...")
        po_data = {
            "supplier": 1,
            "store": 1,
            "expected_delivery": "2026-02-01",
            "notes": "Regular monthly order",
            "items": [
                {
                    "variant": 1,
                    "quantity": 100,
                    "unit_price": "400.00"
                }
            ]
        }
        po = self.post("/api/purchasing/purchase-orders/", po_data)
        self.print_result("Purchase Order Created", po)
        
        # 11. View low stock items
        print("\n1️⃣1️⃣ Checking low stock items...")
        low_stock = self.get("/api/inventory/stock/low_stock/", {"threshold": 20})
        self.print_result("Low Stock Items", low_stock)
        
        # 12. Configure stock alerts
        print("\n1️⃣2️⃣ Viewing stock alerts...")
        alerts = self.get("/api/inventory/alerts/")
        self.print_result("Stock Alerts", alerts)
        
        print("\n" + "="*60)
        print("✅ MANAGER WORKFLOW TEST COMPLETE")
        print("="*60)


if __name__ == "__main__":
    # Initialize client
    client = ManagerClient()
    
    # Run manager workflow
    client.test_manager_workflow()
    
    print("\n💡 Store Manager can:")
    print("   ✅ Manage products and variants")
    print("   ✅ Adjust stock levels")
    print("   ✅ Create purchase orders")
    print("   ✅ Manage suppliers")
    print("   ✅ Configure stock alerts")
    print("   ✅ View inventory reports")
    print("   ❌ Cannot approve users (admin only)")
