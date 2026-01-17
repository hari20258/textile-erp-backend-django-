"""
Admin Client - Full system access
Tests all administrative operations
"""
from base_client import BaseAPIClient


class AdminClient(BaseAPIClient):
    """Client for Admin user operations"""
    
    def test_admin_workflow(self):
        """Complete admin workflow test"""
        
        print("\n" + "="*60)
        print("🔑 ADMIN USER TESTING")
        print("="*60)
        
        # 1. Login as admin
        print("\n1️⃣ Logging in as admin...")
        login_result = self.login("admin", "admin123")
        self.print_result("Admin Login", login_result)
        
        # 2. View profile
        print("\n2️⃣ Getting admin profile...")
        profile = self.get("/api/users/profile/")
        self.print_result("Admin Profile", profile)
        
        # 3. Create a store
        print("\n3️⃣ Creating a new store...")
        store_data = {
            "name": "Downtown Store",
            "code": "DT001", 
            "store_type": "RETAIL",
            "address": "123 Main St, City",
            "phone": "+1234567890",
            "is_active": True
        }
        store = self.post("/api/users/stores/", store_data)
        self.print_result("New Store Created", store)
        store_id = store.get('id')
        
        # 4. List all users
        print("\n4️⃣ Listing all users...")
        users = self.get("/api/users/list/")
        self.print_result("All Users", users)
        
        # 5. Approve a customer (assuming one exists)
        print("\n5️⃣ Approving users...")
        # This would approve a specific user by ID
        print("✅ User approval endpoint: POST /api/users/{id}/approve/")
        
        # 6. Create category
        print("\n6️⃣ Creating product category...")
        category_data = {
            "name": "Men's Wear",
            "description": "Men's clothing and accessories"
        }
        category = self.post("/api/catalog/categories/", category_data)
        self.print_result("New Category", category)
        category_id = category.get('id')
        
        # 7. Create product
        print("\n7️⃣ Creating product...")
        product_data = {
            "name": "Premium Cotton Shirt",
            "description": "High quality cotton shirt",
            "category": category_id,
            "brand": "Premium Textiles",
            "base_price": "999.00"
        }
        product = self.post("/api/catalog/products/", product_data)
        self.print_result("New Product", product)
        product_id = product.get('id')
        
        # 8. Create product variant
        print("\n8️⃣ Creating product variant...")
        variant_data = {
            "product": product_id,
            "sku": "PCS-M-BLUE-001",
            "size": "M",
            "color": "Blue",
            "fabric_type": "Cotton",
            "retail_price": "1299.00",
            "wholesale_price": "999.00",
            "min_wholesale_qty": 10,
            "weight": "0.25"
        }
        variant = self.post("/api/catalog/variants/", variant_data)
        self.print_result("New Variant", variant)
        variant_id = variant.get('id')
        
        # 9. View inventory
        print("\n9️⃣ Viewing stock records...")
        stock = self.get("/api/inventory/stock/")
        self.print_result("Stock Records", stock)
        
        # 10. Create stock alert
        if store_id and variant_id:
            print("\n🔟 Creating stock alert...")
            alert_data = {
                "variant": variant_id,
                "location": store_id,
                "threshold": 10,
                "is_active": True
            }
            alert = self.post("/api/inventory/alerts/", alert_data)
            self.print_result("Stock Alert Created", alert)
        
        # 11. View all purchase orders
        print("\n1️⃣1️⃣ Viewing purchase orders...")
        pos = self.get("/api/purchasing/purchase-orders/")
        self.print_result("Purchase Orders", pos)
        
        # 12. View all sales orders
        print("\n1️⃣2️⃣ Viewing sales orders...")
        orders = self.get("/api/sales/orders/")
        self.print_result("Sales Orders", orders)
        
        print("\n" + "="*60)
        print("✅ ADMIN WORKFLOW TEST COMPLETE")
        print("="*60)


if __name__ == "__main__":
    # Initialize client
    client = AdminClient()
    
    # Run admin workflow
    client.test_admin_workflow()
    
    print("\n💡 Admin has access to ALL endpoints in the system!")
    print("   - User management and approval")
    print("   - Store management")
    print("   - Full catalog CRUD")
    print("   - Inventory management")
    print("   - Purchase order oversight")
    print("   - Sales order monitoring")
    print("   - Stock alerts configuration")
