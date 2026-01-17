from django.db import models
from apps.catalog.models import ProductVariant
from apps.users.models import Store, CustomUser


class Supplier(models.Model):
    """Supplier information"""
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'SUPPLIER'},
        related_name='supplier_profile'
    )
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    tax_id = models.CharField(max_length=50, blank=True)
    payment_terms = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., Net 30, Net 60"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['company_name']
    
    def __str__(self):
        return self.company_name


class PurchaseOrder(models.Model):
    """Purchase orders to suppliers"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent to Supplier'),
        ('CONFIRMED', 'Confirmed by Supplier'),
        ('SHIPPED', 'Shipped'),
        ('RECEIVED', 'Received'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    po_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchase_orders'
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.PROTECT,
        related_name='purchase_orders',
        help_text="Receiving location"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    order_date = models.DateField(auto_now_add=True)
    expected_delivery = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_purchase_orders'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"PO #{self.po_number} - {self.supplier.company_name}"
    
    def save(self, *args, **kwargs):
        if not self.po_number:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            last_po = PurchaseOrder.objects.filter(po_number__startswith=f'PO-{date_str}').order_by('-po_number').first()
            if last_po:
                last_num = int(last_po.po_number.split('-')[-1])
                self.po_number = f'PO-{date_str}-{str(last_num + 1).zfill(4)}'
            else:
                self.po_number = f'PO-{date_str}-0001'
        super().save(*args, **kwargs)


class PurchaseOrderItem(models.Model):
    """Line items in purchase order"""
    
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items'
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name='purchase_order_items'
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    class Meta:
        ordering = ['purchase_order', 'id']
    
    def __str__(self):
        return f"{self.variant.sku} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class GoodsReceiptNote(models.Model):
    """Goods receipt note for tracking received items"""
    
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.PROTECT,
        related_name='grns'
    )
    grn_number = models.CharField(max_length=50, unique=True)
    received_date = models.DateField(auto_now_add=True)
    received_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='received_grns'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Goods Receipt Note'
        verbose_name_plural = 'Goods Receipt Notes'
    
    def __str__(self):
        return f"GRN #{self.grn_number}"
    
    def save(self, *args, **kwargs):
        if not self.grn_number:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            last_grn = GoodsReceiptNote.objects.filter(grn_number__startswith=f'GRN-{date_str}').order_by('-grn_number').first()
            if last_grn:
                last_num = int(last_grn.grn_number.split('-')[-1])
                self.grn_number = f'GRN-{date_str}-{str(last_num + 1).zfill(4)}'
            else:
                self.grn_number = f'GRN-{date_str}-0001'
        super().save(*args, **kwargs)


class GRNItem(models.Model):
    """Line items in goods receipt note"""
    
    grn = models.ForeignKey(
        GoodsReceiptNote,
        on_delete=models.CASCADE,
        related_name='items'
    )
    po_item = models.ForeignKey(
        PurchaseOrderItem,
        on_delete=models.PROTECT,
        related_name='grn_items'
    )
    quantity_received = models.PositiveIntegerField()
    quantity_rejected = models.PositiveIntegerField(default=0)
    remarks = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.po_item.variant.sku} - Received: {self.quantity_received}"
