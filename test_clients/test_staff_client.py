"""
Sales Staff Client - Order processing and sales
Tests sales staff operations
"""
from base_client import BaseAPIClient


class SalesStaffClient(BaseAPIClient):
    """Client for Sales Staff operations"""
    
    def test_staff_workflow(self):
        """Complete sales staff workflow test"""
        
        print("\n" + "="*60)
        print("🛒 SALES STAFF TESTING")
        print("="*60)
        
        # 1. Login as sales staff
        print("\n1️⃣ Logging in as sales staff...")
        login_result = self.login("staff1", "staff123")
        self.print_result("Staff Login", login_result)
        
        # 2. View profile
        print("\n2️⃣ Getting staff profile...")
        profile = self.get("/api/users/profile/")
        self.print_result("Staff Profile", profile)
        
        # 3. Browse products
        print("\n3️⃣ Browsing product catalog...")
        products = self.get("/api/catalog/products/")
        self.print_result("Available Products", products)
        
        # 4. Check product availability
        print("\n4️⃣ Checking variant details...")
        variants = self.get("/api/catalog/variants/", {"color": "Blue"})
        self.print_result("Blue Variants", variants)
        
        # 5. Check stock availability
        print("\n5️⃣ Checking stock availability...")
        stock = self.get("/api/inventory/stock/")
        self.print_result("Stock Levels", stock)
        
        # 6. Create retail order
        print("\n6️⃣ Creating retail order...")
        retail_order_data = {
            "customer": 2,  # Assuming customer exists
            "order_type": "RETAIL",
            "store": 1,
            "delivery_date": "2026-01-25",
            "discount": "0.00",
            "notes": "Walk-in customer purchase",
            "items": [
                {
                    "variant": 1,
                    "quantity": 2
                }
            ]
        }
        retail_order = self.post("/api/sales/orders/", retail_order_data)
        self.print_result("Retail Order Created", retail_order)
        retail_order_id = retail_order.get('id')
        
        # 7. Create wholesale order
        print("\n7️⃣ Creating wholesale order...")
        wholesale_order_data = {
            "customer": 3,  # Assuming wholesale customer exists
            "order_type": "WHOLESALE",
            "store": 1,
            "delivery_date": "2026-02-01",
            "discount": "50.00",
            "notes": "Bulk order - regular customer",
            "items": [
                {
                    "variant": 1,
                    "quantity": 50  # Meets wholesale minimum
                }
            ]
        }
        wholesale_order = self.post("/api/sales/orders/", wholesale_order_data)
        self.print_result("Wholesale Order Created", wholesale_order)
        wholesale_order_id = wholesale_order.get('id')
        
        # 8. Confirm order (triggers stock decrement)
        if retail_order_id:
            print("\n8️⃣ Confirming retail order...")
            confirm = self.post(f"/api/sales/orders/{retail_order_id}/confirm/", {})
            self.print_result("Order Confirmed", confirm)
        
        # 9. Mark order as shipped
        if retail_order_id:
            print("\n9️⃣ Marking order as shipped...")
            shipped = self.post(f"/api/sales/orders/{retail_order_id}/mark_shipped/", {})
            self.print_result("Order Shipped", shipped)
        
        # 10. Mark order as delivered
        if retail_order_id:
            print("\n🔟 Marking order as delivered...")
            delivered = self.post(f"/api/sales/orders/{retail_order_id}/mark_delivered/", {})
            self.print_result("Order Delivered", delivered)
        
        # 11. View all orders
        print("\n1️⃣1️⃣ Viewing all orders...")
        all_orders = self.get("/api/sales/orders/")
        self.print_result("All Orders", all_orders)
        
        # 12. View invoices
        print("\n1️⃣2️⃣ Viewing invoices...")
        invoices = self.get("/api/sales/invoices/")
        self.print_result("Invoices", invoices)
        
        # 13. Record payment
        print("\n1️⃣3️⃣ Recording payment...")
        payment_data = {
            "invoice": 1,  # Assuming invoice exists
            "amount": "1500.00",
            "payment_method": "CARD",
            "reference_number": "TXN123456789",
            "notes": "Paid via credit card"
        }
        payment = self.post("/api/sales/payments/", payment_data)
        self.print_result("Payment Recorded", payment)
        
        # 14. Cancel an order (if needed)
        if wholesale_order_id:
            print("\n1️⃣4️⃣ Canceling wholesale order...")
            cancel = self.post(f"/api/sales/orders/{wholesale_order_id}/cancel/", {})
            self.print_result("Order Cancelled", cancel)
        
        print("\n" + "="*60)
        print("✅ SALES STAFF WORKFLOW TEST COMPLETE")
        print("="*60)


if __name__ == "__main__":
    # Initialize client
    client = SalesStaffClient()
    
    # Run sales staff workflow
    client.test_staff_workflow()
    
    print("\n💡 Sales Staff can:")
    print("   ✅ Browse products and check availability")
    print("   ✅ Create retail and wholesale orders")
    print("   ✅ Confirm orders (decrements stock)")
    print("   ✅ Update order status (shipped, delivered)")
    print("   ✅ Cancel orders (releases stock)")
    print("   ✅ View and create invoices")
    print("   ✅ Record payments")
    print("   ❌ Cannot modify products or adjust stock")
    print("   ❌ Cannot create purchase orders")
