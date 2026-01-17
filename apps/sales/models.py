from django.db import models
from apps.catalog.models import ProductVariant
from apps.users.models import Store, CustomUser


class Order(models.Model):
    """Sales orders (retail and wholesale)"""
    
    ORDER_TYPE_CHOICES = [
        ('RETAIL', 'Retail'),
        ('WHOLESALE', 'Wholesale'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='RETAIL')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateField(null=True, blank=True)
    store = models.ForeignKey(
        Store,
        on_delete=models.PROTECT,
        related_name='orders',
        help_text="Fulfillment location"
    )
    
    # Pricing (removed tax as per user requirement)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_orders',
        help_text="Sales staff who created the order"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.customer.username}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            last_order = Order.objects.filter(order_number__startswith=f'SO-{date_str}').order_by('-order_number').first()
            if last_order:
                last_num = int(last_order.order_number.split('-')[-1])
                self.order_number = f'SO-{date_str}-{str(last_num + 1).zfill(4)}'
            else:
                self.order_number = f'SO-{date_str}-0001'
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Line items in sales order"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.variant.sku} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Invoice(models.Model):
    """Invoice for sales order"""
    
    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name='invoice'
    )
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice #{self.invoice_number}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            last_inv = Invoice.objects.filter(invoice_number__startswith=f'INV-{date_str}').order_by('-invoice_number').first()
            if last_inv:
                last_num = int(last_inv.invoice_number.split('-')[-1])
                self.invoice_number = f'INV-{date_str}-{str(last_num + 1).zfill(4)}'
            else:
                self.invoice_number = f'INV-{date_str}-0001'
        
        self.balance = self.amount - self.paid_amount
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment records for invoices"""
    
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('UPI', 'UPI'),
        ('CHEQUE', 'Cheque'),
    ]
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Payment {self.amount} for {self.invoice.invoice_number}"
