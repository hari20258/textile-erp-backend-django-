# Test Clients for Textile Backend API

A collection of Python clients to test all API endpoints for each user role.

## Setup

1. **Install requests library**:
```bash
pip install requests
```

2. **Start the Django server**:
```bash
cd ..
source venv/bin/activate
python manage.py runserver
```

3. **Create test data** (in Django admin or via API):
- Create a superuser (admin)
- Create test users for each role
- Create at least one store
- Create some products and variants

## Usage

Run each client file to test specific user role:

```bash
# Test Admin operations
python test_admin_client.py

# Test Store Manager operations
python test_manager_client.py

# Test Sales Staff operations
python test_staff_client.py

# Test Supplier operations
python test_supplier_client.py

# Test Customer operations
python test_customer_client.py
```

## Test User Credentials

Create these users in Django admin first:

| Username   | Password     | Role          |
|------------|--------------|---------------|
| admin      | admin123     | ADMIN         |
| manager1   | manager123   | STORE_MANAGER |
| staff1     | staff123     | SALES_STAFF   |
| supplier1  | supplier123  | SUPPLIER      |
| customer1  | customer123  | CUSTOMER      |

## What Each Client Tests

### 1. Admin Client (`test_admin_client.py`)
- ✅ User management and approval
- ✅ Store creation and management
- ✅ Complete catalog CRUD
- ✅ Inventory oversight
- ✅ Purchase and sales monitoring
- ✅ Stock alert configuration

### 2. Manager Client (`test_manager_client.py`)
- ✅ Product and variant management
- ✅ Stock adjustments (atomic operations)
- ✅ Purchase order creation
- ✅ Supplier management
- ✅ Inventory monitoring
- ✅ Stock alert setup

### 3. Sales Staff Client (`test_staff_client.py`)
- ✅ Product browsing
- ✅ Order creation (retail/wholesale)
- ✅ Order confirmation (stock decrement)
- ✅ Order status updates
- ✅ Invoice management
- ✅ Payment recording
- ✅ Order cancellation

### 4. Supplier Client (`test_supplier_client.py`)
- ✅ View assigned purchase orders
- ✅ Confirm received orders
- ✅ Update shipment status
- ✅ PO history and details

### 5. Customer Client (`test_customer_client.py`)
- ✅ Registration
- ✅ Product browsing and filtering
- ✅ Order placement (if approved)
- ✅ Order history viewing

## Key Features Demonstrated

### Atomic Stock Operations
- **Order Creation**: Reserves stock atomically
- **Order Confirmation**: Decrements stock and releases reservation
- **Order Cancellation**: Releases or restores stock
- **Stock Adjustment**: Manual stock changes with locking
- **GRN**: Automatic stock increment on goods receipt

### Role-Based Access Control
Each client demonstrates the permissions for that role:
- Admin: Full access
- Manager: Product, inventory, purchasing
- Staff: Sales operations only
- Supplier: Own POs only
- Customer: Browse and order only

### Dual Pricing
- Retail orders use `retail_price`
- Wholesale orders use `wholesale_price` (with minimum quantity validation)

## Notes

- Clients use JWT authentication (stored in session)
- All responses are pretty-printed for readability
- Error responses include status codes
- Clients demonstrate the complete workflow for each role
- IDs (store, product, variant) may need adjustment based on your data

## Customization

Modify the test data in each client file:
- Change usernames/passwords
- Adjust store IDs
- Update product/variant IDs
- Modify order quantities
- Change filtering parameters
