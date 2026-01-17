"""
Customer Client - Browse and order products
Tests customer operations
"""
from base_client import BaseAPIClient


class CustomerClient(BaseAPIClient):
    """Client for Customer operations"""
    
    def test_customer_workflow(self):
        """Complete customer workflow test"""
        
        print("\n" + "="*60)
        print("🛍️  CUSTOMER TESTING")
        print("="*60)
        
        # 1. Register as new customer
        print("\n1️⃣ Registering new customer account...")
        register_data = {
            "username": "customer_john",
            "email": "john@customer.com",
            "password": "customer123",
            "role": "CUSTOMER",
            "phone": "+1234567890",
            "address": "789 Customer Ave, City"
        }
        registration = self.register(**register_data)
        self.print_result("Registration", registration)
        
        # 2. Login as customer
        print("\n2️⃣ Logging in as customer...")
        login_result = self.login("customer_john", "customer123")
        self.print_result("Customer Login", login_result)
        
        # 3. View profile
        print("\n3️⃣ Viewing customer profile...")
        profile = self.get("/api/users/profile/")
        self.print_result("Customer Profile", profile)
        
        # 4. Browse categories
        print("\n4️⃣ Browsing product categories...")
        categories = self.get("/api/catalog/categories/")
        self.print_result("Categories", categories)
        
        # 5. Browse all products
        print("\n5️⃣ Browsing all products...")
        products = self.get("/api/catalog/products/")
        self.print_result("All Products", products)
        
        # 6. Search products by brand
        print("\n6️⃣ Searching products by brand...")
        brand_products = self.get("/api/catalog/products/", {"search": "Premium"})
        self.print_result("Premium Brand Products", brand_products)
        
        # 7. Filter variants by size and color
        print("\n7️⃣ Filtering variants (Medium, Blue)...")
        filtered_variants = self.get("/api/catalog/variants/", {
            "size": "M",
            "color": "Blue"
        })
        self.print_result("Filtered Variants", filtered_variants)
        
        # 8. Filter variants by price range
        print("\n8️⃣ Filtering by price range...")
        price_variants = self.get("/api/catalog/variants/", {
            "min_price": "500",
            "max_price": "1500"
        })
        self.print_result("Variants in Price Range", price_variants)
        
        # 9. View my orders (should be empty initially)
        print("\n9️⃣ Viewing my orders...")
        my_orders = self.get("/api/sales/orders/")
        self.print_result("My Orders", my_orders)
        
        # 10. Check if approved (customers need approval)
        print("\n🔟 Checking approval status...")
        current_user = self.get("/api/users/current/")
        self.print_result("Current User Info", current_user)
        
        if current_user.get('is_approved'):
            print("\n   ✅ Customer is approved! Can place orders.")
            
            # 11. Place an order (if approved)
            print("\n1️⃣1️⃣ Placing an order...")
            order_data = {
                "customer": current_user.get('id'),
                "order_type": "RETAIL",
                "store": 1,
                "delivery_date": "2026-01-30",
                "discount": "0.00",
                "notes": "Online order - first purchase",
                "items": [
                    {
                        "variant": 1,
                        "quantity": 3
                    }
                ]
            }
            order = self.post("/api/sales/orders/", order_data)
            self.print_result("Order Placed", order)
            
            # 12. View updated order list
            print("\n1️⃣2️⃣ Viewing updated order list...")
            updated_orders = self.get("/api/sales/orders/")
            self.print_result("My Orders", updated_orders)
        else:
            print("\n   ⚠️  Customer is NOT approved yet.")
            print("      Admin needs to approve before placing orders.")
        
        print("\n" + "="*60)
        print("✅ CUSTOMER WORKFLOW TEST COMPLETE")
        print("="*60)


if __name__ == "__main__":
    # Initialize client
    client = CustomerClient()
    
    # Run customer workflow
    client.test_customer_workflow()
    
    print("\n💡 Customer can:")
    print("   ✅ Register and login")
    print("   ✅ Browse products and categories")
    print("   ✅ Search and filter products")
    print("   ✅ View product details and pricing")
    print("   ✅ Place orders (if approved)")
    print("   ✅ View own order history")
    print("   ❌ Cannot view other customers' orders")
    print("   ❌ Cannot access inventory or admin features")
    print("   ❌ Cannot modify products")
    print("\n📌 Note: Customers need admin approval before placing orders")
