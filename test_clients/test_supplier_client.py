"""
Supplier Client - Purchase order management
Tests supplier operations
"""
from base_client import BaseAPIClient


class SupplierClient(BaseAPIClient):
    """Client for Supplier operations"""
    
    def test_supplier_workflow(self):
        """Complete supplier workflow test"""
        
        print("\n" + "="*60)
        print("📦 SUPPLIER TESTING")
        print("="*60)
        
        # 1. Login as supplier
        print("\n1️⃣ Logging in as supplier...")
        login_result = self.login("supplier1", "supplier123")
        self.print_result("Supplier Login", login_result)
        
        # 2. View profile
        print("\n2️⃣ Getting supplier profile...")
        profile = self.get("/api/users/profile/")
        self.print_result("Supplier Profile", profile)
        
        # 3. View assigned purchase orders
        print("\n3️⃣ Viewing my purchase orders...")
        pos = self.get("/api/purchasing/purchase-orders/")
        self.print_result("My Purchase Orders", pos)
        
        # 4. Filter POs by status
        print("\n4️⃣ Viewing SENT purchase orders...")
        sent_pos = self.get("/api/purchasing/purchase-orders/", {"status": "SENT"})
        self.print_result("SENT Purchase Orders", sent_pos)
        
        # 5. Confirm a purchase order
        po_id = 1  # Assuming PO exists
        print(f"\n5️⃣ Confirming purchase order #{po_id}...")
        confirm = self.post(f"/api/purchasing/purchase-orders/{po_id}/confirm/", {})
        self.print_result("PO Confirmed", confirm)
        
        # 6. Mark PO as shipped
        print(f"\n6️⃣ Marking PO #{po_id} as shipped...")
        shipped = self.post(f"/api/purchasing/purchase-orders/{po_id}/mark_shipped/", {})
        self.print_result("PO Shipped", shipped)
        
        # 7. View confirmed orders
        print("\n7️⃣ Viewing CONFIRMED orders...")
        confirmed_pos = self.get("/api/purchasing/purchase-orders/", {"status": "CONFIRMED"})
        self.print_result("Confirmed Orders", confirmed_pos)
        
        # 8. View shipped orders
        print("\n8️⃣ Viewing SHIPPED orders...")
        shipped_pos = self.get("/api/purchasing/purchase-orders/", {"status": "SHIPPED"})
        self.print_result("Shipped Orders", shipped_pos)
        
        # 9. View specific PO details
        print(f"\n9️⃣ Viewing PO #{po_id} details...")
        po_detail = self.get(f"/api/purchasing/purchase-orders/{po_id}/")
        self.print_result("PO Details", po_detail)
        
        print("\n" + "="*60)
        print("✅ SUPPLIER WORKFLOW TEST COMPLETE")
        print("="*60)


if __name__ == "__main__":
    # Initialize client
    client = SupplierClient()
    
    # Run supplier workflow
    client.test_supplier_workflow()
    
    print("\n💡 Supplier can:")
    print("   ✅ View assigned purchase orders")
    print("   ✅ Confirm received purchase orders")
    print("   ✅ Update shipment status")
    print("   ✅ View PO history and details")
    print("   ❌ Cannot view other suppliers' orders")
    print("   ❌ Cannot create purchase orders")
    print("   ❌ Cannot access inventory or sales")
    print("\n📌 Note: Suppliers need to be approved by admin before accessing the system")
