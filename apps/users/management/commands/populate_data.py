"""
Management command to populate database with sample data
Usage: python manage.py populate_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.users.models import CustomUser, Store
from apps.catalog.models import Category, Product, ProductVariant
from apps.inventory.models import StockRecord, StockTransaction
from apps.purchasing.models import Supplier, PurchaseOrder, PurchaseOrderItem
from apps.sales.models import Order, OrderItem
import random
from decimal import Decimal
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # 1. Create Stores
        self.stdout.write('Creating stores...')
        main_store, _ = Store.objects.get_or_create(
            name="Main Retail Store",
            defaults={
                "code": "MRS-001",
                "store_type": "RETAIL",
                "address": "123 Fashion Ave, Mumbai",
                "phone": "+91 9876543210",
                "is_active": True
            }
        )
        
        warehouse, _ = Store.objects.get_or_create(
            name="Central Warehouse",
            defaults={
                "code": "WH-001",
                "store_type": "WAREHOUSE",
                "address": "456 Logistics Park, Bhiwandi",
                "phone": "+91 9876543211",
                "is_active": True
            }
        )

        # 2. Create Users
        self.stdout.write('Creating users...')
        users = {}
        
        # Admin
        if not CustomUser.objects.filter(username='admin').exists():
            CustomUser.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            
        # Manager
        users['manager'], _ = CustomUser.objects.get_or_create(
            username='manager1',
            defaults={
                'email': 'manager@example.com',
                'role': 'STORE_MANAGER',
                'store': main_store,
                'is_approved': True
            }
        )
        if _: users['manager'].set_password('manager123'); users['manager'].save()
        
        # Staff
        users['staff'], _ = CustomUser.objects.get_or_create(
            username='staff1',
            defaults={
                'email': 'staff@example.com',
                'role': 'SALES_STAFF',
                'store': main_store,
                'is_approved': True
            }
        )
        if _: users['staff'].set_password('staff123'); users['staff'].save()
        
        # Supplier User
        users['supplier_user'], _ = CustomUser.objects.get_or_create(
            username='supplier1',
            defaults={
                'email': 'supplier@example.com',
                'role': 'SUPPLIER',
                'is_approved': True
            }
        )
        if _: users['supplier_user'].set_password('supplier123'); users['supplier_user'].save()
        
        # Customer User
        users['customer'], _ = CustomUser.objects.get_or_create(
            username='customer1',
            defaults={
                'email': 'customer@example.com',
                'role': 'CUSTOMER',
                'is_approved': True
            }
        )
        if _: users['customer'].set_password('customer123'); users['customer'].save()

        # 3. Create Categories
        self.stdout.write('Creating categories...')
        categories = {}
        cats = ['Men', 'Women', 'Kids', 'Fabric']
        for name in cats:
            categories[name], _ = Category.objects.get_or_create(name=name)
            
        # Subcategories
        Category.objects.get_or_create(name="Shirts", parent=categories['Men'])
        Category.objects.get_or_create(name="Sarees", parent=categories['Women'])
        Category.objects.get_or_create(name="Denim", parent=categories['Fabric'])

        # 4. Create Products & Variants
        self.stdout.write('Creating products...')
        
        products_data = [
            {
                "name": "Classic Cotton Shirt",
                "category": categories['Men'],
                "brand": "Raymond",
                "base_price": 1200,
                "variants": [
                    {"size": "M", "color": "Blue", "sku": "SH-M-BLU", "retail": 1500, "wholesale": 1000},
                    {"size": "L", "color": "White", "sku": "SH-L-WHT", "retail": 1600, "wholesale": 1100}
                ]
            },
            {
                "name": "Silk Saree",
                "category": categories['Women'],
                "brand": "Nalli",
                "base_price": 5000,
                "variants": [
                    {"size": "CUSTOM", "color": "Red", "sku": "SAR-RED", "retail": 8000, "wholesale": 6000},
                    {"size": "CUSTOM", "color": "Green", "sku": "SAR-GRN", "retail": 8500, "wholesale": 6500}
                ]
            }
        ]
        
        variants_created = []
        for p_data in products_data:
            p, _ = Product.objects.get_or_create(
                name=p_data['name'],
                defaults={
                    "category": p_data['category'],
                    "brand": p_data['brand'],
                    "base_price": p_data['base_price']
                }
            )
            
            for v_data in p_data['variants']:
                v, created = ProductVariant.objects.get_or_create(
                    sku=v_data['sku'],
                    defaults={
                        "product": p,
                        "size": v_data['size'],
                        "color": v_data['color'],
                        "fabric_type": "Cotton/Silk",
                        "retail_price": v_data['retail'],
                        "wholesale_price": v_data['wholesale'],
                        "min_wholesale_qty": 10,
                        "weight": 0.5
                    }
                )
                variants_created.append(v)

        # 5. Inventory (Stock)
        self.stdout.write('Initializing stock...')
        for variant in variants_created:
            # Add stock to main store
            StockRecord.objects.get_or_create(
                variant=variant,
                location=main_store,
                defaults={'quantity': 100, 'reserved_quantity': 0}
            )
            # Add stock to warehouse
            StockRecord.objects.get_or_create(
                variant=variant,
                location=warehouse,
                defaults={'quantity': 500, 'reserved_quantity': 0}
            )

        # 6. Supplier
        self.stdout.write('Creating supplier profile...')
        supplier, _ = Supplier.objects.get_or_create(
            user=users['supplier_user'],
            defaults={
                "company_name": "Best Textiles Ltd",
                "contact_person": "Rajesh Kumar",
                "phone": "+91 9988776655",
                "email": "rajesh@besttextiles.com",
                "is_active": True
            }
        )

        # 7. Purchase Order
        self.stdout.write('Creating sample purchase order...')
        if not PurchaseOrder.objects.exists():
            po = PurchaseOrder.objects.create(
                supplier=supplier,
                store=warehouse,
                status='CONFIRMED',
                created_by=users['manager'],
                expected_delivery=timezone.now().date() + timedelta(days=7),
                notes="Initial bulk stock"
            )
            
            total = 0
            for variant in variants_created[:2]:
                qty = 50
                price = variant.wholesale_price * Decimal('0.8') # Supplier price
                line_total = qty * price
                total += line_total
                
                PurchaseOrderItem.objects.create(
                    purchase_order=po,
                    variant=variant,
                    quantity=qty,
                    unit_price=price,
                    line_total=line_total
                )
            
            po.total_amount = total
            po.save()

        # 8. Sales Order
        self.stdout.write('Creating sample sales order...')
        if not Order.objects.exists():
            order = Order.objects.create(
                customer=users['customer'],
                store=main_store,
                order_type='RETAIL',
                status='PENDING',
                created_by=users['staff'],
                delivery_date=timezone.now().date() + timedelta(days=2),
                notes="Sample retail order"
            )
            
            subtotal = 0
            for variant in variants_created[:1]:
                qty = 2
                price = variant.retail_price
                line_total = qty * price
                subtotal += line_total
                
                OrderItem.objects.create(
                    order=order,
                    variant=variant,
                    quantity=qty,
                    unit_price=price,
                    line_total=line_total
                )
                
                # Reserve stock (mimicking the serializer logic)
                stock = StockRecord.objects.get(variant=variant, location=main_store)
                stock.reserved_quantity += qty
                stock.save()
            
            order.subtotal = subtotal
            order.total_amount = subtotal
            order.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample data!'))
        self.stdout.write(self.style.SUCCESS(f'Created {len(variants_created)} variants across {len(products_data)} products.'))
