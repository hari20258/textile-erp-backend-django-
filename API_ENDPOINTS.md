# API Endpoints Reference

Base URL: `http://localhost:8000/api/`

## 🔐 Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/token/` | Obtain JWT access & refresh tokens |
| POST | `/api/auth/token/refresh/` | Refresh expired access token |

## 👤 Users App (`/api/users/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/register/` | Register new user |
| GET | `/api/users/profile/` | Get current user's profile |
| PUT | `/api/users/profile/` | Update current user's profile |
| GET | `/api/users/current/` | Get current user info (lightweight) |
| GET | `/api/users/list/` | List all users (Manager/Admin only) |
| POST | `/api/users/{id}/approve/` | Approve a user (Admin only) |
| GET | `/api/users/stores/` | List all stores |
| POST | `/api/users/stores/` | Create new store |
| GET | `/api/users/stores/{id}/` | Get store details |
| PUT | `/api/users/stores/{id}/` | Update store |
| DELETE | `/api/users/stores/{id}/` | Delete store |

## 📦 Catalog App (`/api/catalog/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/catalog/categories/` | List categories |
| POST | `/api/catalog/categories/` | Create category |
| GET | `/api/catalog/categories/{id}/` | Get category details |
| GET | `/api/catalog/products/` | List products (filterable) |
| POST | `/api/catalog/products/` | Create product |
| GET | `/api/catalog/products/{id}/` | Get product details |
| GET | `/api/catalog/variants/` | List product variants (SKUs) |
| POST | `/api/catalog/variants/` | Create variant |
| GET | `/api/catalog/variants/{id}/` | Get variant details |

## 🏭 Inventory App (`/api/inventory/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/inventory/stock/` | View all stock records |
| GET | `/api/inventory/stock/low_stock/` | Get low stock items (Custom Action) |
| GET | `/api/inventory/stock/{id}/` | Get specific stock record |
| GET | `/api/inventory/transactions/` | View stock transaction history |
| GET | `/api/inventory/transactions/{id}/` | Get transaction details |
| POST | `/api/inventory/adjust/` | **Atomic** manual stock adjustment |
| GET | `/api/inventory/alerts/` | List stock alerts |
| POST | `/api/inventory/alerts/` | Create stock alert |
| GET | `/api/inventory/alerts/triggered/` | Get currently triggered alerts (Custom Action) |

## 🚚 Purchasing App (`/api/purchasing/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/purchasing/suppliers/` | List suppliers |
| POST | `/api/purchasing/suppliers/` | Create supplier |
| GET | `/api/purchasing/suppliers/{id}/` | Get supplier details |
| GET | `/api/purchasing/purchase-orders/` | List purchase orders |
| POST | `/api/purchasing/purchase-orders/` | Create purchase order |
| POST | `/api/purchasing/purchase-orders/{id}/send_to_supplier/` | Mark PO as sent (Custom Action) |
| POST | `/api/purchasing/purchase-orders/{id}/confirm/` | Supplier confirms PO (Custom Action) |
| POST | `/api/purchasing/purchase-orders/{id}/mark_shipped/` | Supplier marks shipped (Custom Action) |
| GET | `/api/purchasing/grn/` | List Goods Receipt Notes |
| POST | `/api/purchasing/grn/` | Create GRN (triggers **Atomic Stock Increment**) |
| GET | `/api/purchasing/grn/{id}/` | Get GRN details |

## 🛒 Sales App (`/api/sales/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sales/orders/` | List sales orders |
| POST | `/api/sales/orders/` | Create order (triggers **Stock Reservation**) |
| GET | `/api/sales/orders/{id}/` | Get order details |
| POST | `/api/sales/orders/{id}/confirm/` | Confirm order (triggers **Stock Decrement**) |
| POST | `/api/sales/orders/{id}/cancel/` | Cancel order (releases reservation) |
| POST | `/api/sales/orders/{id}/mark_shipped/` | Mark order as shipped |
| POST | `/api/sales/orders/{id}/mark_delivered/` | Mark order as delivered |
| GET | `/api/sales/invoices/` | List invoices |
| GET | `/api/sales/invoices/{id}/` | Get invoice details |
| GET | `/api/sales/payments/` | List payments |
| POST | `/api/sales/payments/` | Record payment (updates balance) |

## 💡 Notes
- All endpoints except `/api/users/register/` and `/api/auth/token/` require **Authentication** header.
- Use `Authorization: Bearer <your_access_token>` header.
- List endpoints support pagination (e.g., `?page=2`).
- Search is available on most list endpoints via `?search=query`.
- Filtering is available via query params (e.g., `?category=1`, `?status=PENDING`).
