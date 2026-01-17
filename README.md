# Textile ERP System - Django REST Framework

A robust, enterprise-grade Django REST Framework backend designed for textile retail and wholesale operations. This system manages multi-location inventory, complex product variants (Size/Color/Fabric), procurement lifecycles, and secure sales processing.

---

## 🚀 Key Features

*   **Multi-Store Inventory:** Manage stock across Central Warehouses and Retail Branches with atomic consistency.
*   **Complex Catalog:** Handle textile-specific variants (SKUs) with attributes like Fabric Type, GSM, Color, and Size.
*   **Procurement Flow:** Complete B2B workflow: `Purchase Order` -> `Supplier Confirmation` -> `Goods Receipt (GRN)` -> `Stock Update`.
*   **Role-Based Access Control (RBAC):** Strict isolation for Admins, Store Managers, Sales Staff, Suppliers, and Customers.
*   **Sales & POS:** Real-time stock reservation, wholesale/retail pricing logic, and invoicing.

---

## 👥 User Roles & Responsibilities

| Role | Responsibilities | Key Capabilities |
| :--- | :--- | :--- |
| **Admin** | System Owner | Full access to all stores, users, and settings. |
| **Store Manager** | Branch Head | Manage efficiently *their* store's inventory, staff, and purchases. **Cannot access other stores.** |
| **Sales Staff** | Employee | Create sales orders, view stock for *their* store. |
| **Supplier** | Vendor | View assigned Purchase Orders, confirm orders, mark as shipped. |
| **Customer** | End User | Browse catalog, view *own* orders, track status. |

---

## 🔄 Core Workflows

### 1. Catalog Management (Creating Products)
*Actors: Admin, Store Manager*

Before selling, you must define what you are selling.
1.  **Create Category:** (e.g., "Shirts", "Fabrics"). hierarchy support available.
2.  **Create Product:** Define the base item (e.g., "Cotton Formal Shirt").
3.  **Create Variants:** Define the specific SKUs (e.g., "Red - Size M", "Blue - Size L").
    *   *Note:* Creating a variant does **NOT** add stock. It just defines the item existence. Stock is 0 by default.

### 2. The Restocking Process (How to Fix "Out of Stock")
*Actors: Store Manager, Supplier*

If stock is 0, you cannot sell. You must "buy" or "receive" goods.

**Step A: Create Purchase Order (PO)**
1.  Manager logs in.
2.  Goes to `/api/purchasing/orders/`.
3.  Creates a PO for a specific **Supplier**.
4.  *Status:* `PENDING`.

**Step B: Confirm Order**
1.  Supplier (or Manager mimicking Supplier) views the PO.
2.  Updates Status to `CONFIRMED`.
3.  Updates Status to `SHIPPED` when goods leave.

**Step C: Receive Goods (GRN)**
*This is the critical step that updates inventory!*
1.  Manager goes to `/api/purchasing/grn/` (Goods Receipt Note).
2.  Selects the **Confirmed PO**.
3.  clicks **POST** (Receive All).
4.  **System Action:**
    *   Verifies quantities.
    *   Automatically creates/updates `StockRecord` for that Store.
    *   Increases quantity available.

### 3. Sales Process (Selling Items)
*Actors: Sales Staff, Customer*

**Scenario A: Staff Selling in Store**
1.  Staff creates an Order via `/api/sales/orders/`.
2.  **Store Lock:** System *automatically* forces the Order to be created in the Staff's assigned store (e.g., "Main Branch"). They cannot sell "Central Warehouse" stock.
3.  **Stock Check:** System checks if `StockRecord` > requested quantity.
4.  **Reservation:** Stock is "Reserved" (deducted from Available, added to Reserved).
5.  **Confirmation:** Staff marks order `CONFIRMED`. Stock is permanently deducted.

**Scenario B: Customer Buying Online**
1.  Customer creates Order.
2.  **Isolation:** They see *only* their own orders.
3.  **Store Assignment:** Orders are routed to the default store (or selected store).
4.  Staff reviews and processes the order.

---

## 🛠 scenarios & Troubleshooting

### Scenario: "I created a product but stock is 0"
**Reason:** Catalog != Inventory. You defined the *idea* of the shirt, but you haven't put any physical shirts on the shelf.
**Fix:** Perform the **Restocking Process** (PO -> GRN) or do a manual **Stock Adjustment**.

### Scenario: "Manager sees 'No stock available' but Admin sees stock"
**Reason:** Store Mismatch.
*   The Stock is sitting in "Central Warehouse".
*   The Manager controls "Retail Store A".
**Fix:** Move stock from Warehouse to Store (via Transfer) OR ensure the Manager is ordering for the correct location where stock exists.

### Scenario: "Customer can see other people's orders"
**Security:** This is **blocked**. The system uses a "Deny by Default" strategy.
*   Customers requesting the Order List will receive an **empty list** unless the order belongs specifically to their User ID.

---

## ⚙️ Setup & Installation

1.  **Clone Repo:**
    ```bash
    git clone https://github.com/yourusername/victex-backend.git
    cd victex-backend
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Database Migration:**
    ```bash
    python manage.py migrate
    ```

4.  **Create Superuser:**
    ```bash
    python manage.py createsuperuser
    ```

5.  **Run Server:**
    ```bash
    python manage.py runserver
    ```


