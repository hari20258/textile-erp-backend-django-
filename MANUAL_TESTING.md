# Manual Testing Guide - Textile Backend API

Complete step-by-step guide to test the API manually.

## Part 1: Database Setup (One-Time)

### Step 1: Create PostgreSQL Database

```bash
# Open PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE textile_db;

# Exit
\q
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file and update:
# DB_PASSWORD=your_postgres_password
```

### Step 3: Run Migrations

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate

# You should see output like:
# Running migrations:
#   Applying users.0001_initial... OK
#   Applying catalog.0001_initial... OK
#   ... etc
```

---

## Part 2: Create Test Users (One-Time)

### Method 1: Using Django Admin (Recommended)

```bash
# Create superuser
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: admin123

# Start server
python manage.py runserver

# Open browser: http://localhost:8000/admin/
# Login with admin credentials

# In admin panel:
# 1. Create a Store first (Users → Stores → Add Store)
#    - Name: Main Store
#    - Code: MS001
#    - Type: RETAIL
#    - Save

# 2. Create users (Users → Custom Users → Add Custom User)
#    For each role, create:
```

**Manager:**
- Username: `manager1`
- Password: `manager123`
- Email: `manager@example.com`
- Role: `Store Manager`
- Store: Select "Main Store"
- Is approved: ✓ (checked)

**Sales Staff:**
- Username: `staff1`
- Password: `staff123`
- Email: `staff@example.com`
- Role: `Sales Staff`
- Store: Select "Main Store"
- Is approved: ✓ (checked)

**Supplier:**
- Username: `supplier1`
- Password: `supplier123`
- Email: `supplier@example.com`
- Role: `Supplier`
- Is approved: ✓ (checked)

**Customer:**
- Username: `customer1`
- Password: `customer123`
- Email: `customer@example.com`
- Role: `Customer`
- Is approved: ✓ (checked)

### Method 2: Using Python Shell

```bash
python manage.py shell
```

```python
from apps.users.models import CustomUser, Store

# Create store
store = Store.objects.create(
    name="Main Store",
    code="MS001",
    store_type="RETAIL",
    address="123 Main St",
    phone="+1234567890",
    is_active=True
)

# Create users
admin = CustomUser.objects.create_superuser('admin', 'admin@example.com', 'admin123')

manager = CustomUser.objects.create_user(
    username='manager1',
    email='manager@example.com',
    password='manager123',
    role='STORE_MANAGER',
    store=store
)

staff = CustomUser.objects.create_user(
    username='staff1',
    email='staff@example.com',
    password='staff123',
    role='SALES_STAFF',
    store=store
)

supplier = CustomUser.objects.create_user(
    username='supplier1',
    email='supplier@example.com',
    password='supplier123',
    role='SUPPLIER',
    is_approved=True
)

customer = CustomUser.objects.create_user(
    username='customer1',
    email='customer@example.com',
    password='customer123',
    role='CUSTOMER',
    is_approved=True
)

print("✅ All users created!")
```

---

## Part 3: Running Test Clients

### Prerequisites

```bash
# Install requests library
pip install requests

# Make sure Django server is running
python manage.py runserver
```

### Run Individual Tests

Open a NEW terminal (keep server running in first terminal):

```bash
cd test_clients

# Test admin
python test_admin_client.py

# Test manager
python test_manager_client.py

# Test sales staff
python test_staff_client.py

# Test supplier
python test_supplier_client.py

# Test customer
python test_customer_client.py
```

### Run All Tests at Once

```bash
cd test_clients
chmod +x run_all_tests.sh
./run_all_tests.sh
```

---

## Part 4: Manual API Testing with cURL

### 1. Get JWT Token

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Response:
# {
#   "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
# }

# Copy the access token
```

### 2. Use Token to Access Protected Endpoints

```bash
# Replace YOUR_TOKEN with the actual access token
TOKEN="YOUR_TOKEN_HERE"

# Get user profile
curl http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer $TOKEN"

# List products
curl http://localhost:8000/api/catalog/products/ \
  -H "Authorization: Bearer $TOKEN"

# Create category
curl -X POST http://localhost:8000/api/catalog/categories/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Category",
    "description": "Testing via cURL"
  }'
```

---

## Part 5: Manual Testing with Postman

### Setup

1. **Install Postman** (https://www.postman.com/downloads/)

2. **Create New Collection**: "Textile Backend"

### Authentication

1. **Get Token**:
   - Method: `POST`
   - URL: `http://localhost:8000/api/auth/token/`
   - Body (raw JSON):
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
   - Click "Send"
   - Copy the `access` token

2. **Set Collection Auth**:
   - Click on Collection → Authorization
   - Type: Bearer Token
   - Token: Paste your access token

### Test Requests

Create these requests in your collection:

#### Users
- `GET` `/api/users/profile/`
- `GET` `/api/users/list/`
- `GET` `/api/users/stores/`

#### Catalog
- `GET` `/api/catalog/categories/`
- `POST` `/api/catalog/categories/` (Body: `{"name": "Test", "description": "Test"}`)
- `GET` `/api/catalog/products/`
- `GET` `/api/catalog/variants/`

#### Inventory
- `GET` `/api/inventory/stock/`
- `GET` `/api/inventory/transactions/`
- `POST` `/api/inventory/adjust/` (Body: `{"variant": 1, "location": 1, "adjustment": 10, "reason": "Test"}`)

---

## Part 6: Testing Workflow Examples

### Complete Order Workflow

```bash
# 1. Browse products (as customer)
curl http://localhost:8000/api/catalog/products/ \
  -H "Authorization: Bearer $CUSTOMER_TOKEN"

# 2. Create order
curl -X POST http://localhost:8000/api/sales/orders/ \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer": 5,
    "order_type": "RETAIL",
    "store": 1,
    "delivery_date": "2026-01-30",
    "discount": "0.00",
    "items": [
      {"variant": 1, "quantity": 2}
    ]
  }'

# 3. Confirm order (decrements stock)
curl -X POST http://localhost:8000/api/sales/orders/1/confirm/ \
  -H "Authorization: Bearer $STAFF_TOKEN"

# 4. Check stock (should be less now)
curl http://localhost:8000/api/inventory/stock/ \
  -H "Authorization: Bearer $TOKEN"
```

### Purchase Order Workflow

```bash
# 1. Create PO (as manager)
curl -X POST http://localhost:8000/api/purchasing/purchase-orders/ \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "supplier": 1,
    "store": 1,
    "expected_delivery": "2026-02-01",
    "items": [
      {"variant": 1, "quantity": 100, "unit_price": "400.00"}
    ]
  }'

# 2. Send to supplier
curl -X POST http://localhost:8000/api/purchasing/purchase-orders/1/send_to_supplier/ \
  -H "Authorization: Bearer $MANAGER_TOKEN"

# 3. Supplier confirms
curl -X POST http://localhost:8000/api/purchasing/purchase-orders/1/confirm/ \
  -H "Authorization: Bearer $SUPPLIER_TOKEN"

# 4. Create GRN (increments stock)
curl -X POST http://localhost:8000/api/purchasing/grn/ \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "purchase_order": 1,
    "notes": "All items received",
    "items": [
      {
        "po_item": 1,
        "quantity_received": 100,
        "quantity_rejected": 0
      }
    ]
  }'
```

---

## Troubleshooting

### Common Issues

**"Database does not exist"**
```bash
# Create it manually
psql -U postgres -c "CREATE DATABASE textile_db;"
```

**"No module named 'apps'"**
```bash
# Make sure you're in the project root
cd /path/to/Textile_Backend
python manage.py runserver
```

**"401 Unauthorized"**
```bash
# Token expired - get a new one
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**"Pillow is not installed" error**
```bash
# Pillow was removed - this shouldn't happen
# If you see this, the image field wasn't properly removed
```

---

## Quick Start (TL;DR)

```bash
# 1. Setup database
psql -U postgres -c "CREATE DATABASE textile_db;"

# 2. Configure
cp .env.example .env
# Edit .env with your DB password

# 3. Migrate
source venv/bin/activate
python manage.py migrate

# 4. Create admin
python manage.py createsuperuser

# 5. Start server
python manage.py runserver

# 6. Create users via admin panel (http://localhost:8000/admin/)

# 7. Test APIs
cd test_clients
pip install requests
python test_admin_client.py
```

---

## Next Steps

1. ✅ Set up database and run migrations
2. ✅ Create test users
3. ✅ Run Python test clients
4. 📝 Add more test data (products, variants, stock)
5. 🧪 Test complete workflows (order → confirm → ship)
6. 📊 Monitor stock transactions
7. 🔍 Test edge cases (insufficient stock, etc.)

## Tips

- **Use Django admin** for quick data viewing
- **Check logs** in terminal where server runs
- **Test atomic operations** (create order, check stock reservation)
- **Try different roles** to verify permissions
- **Monitor database** with `psql textile_db` for direct queries
