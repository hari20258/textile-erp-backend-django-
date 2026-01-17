from django.db import models
from apps.catalog.models import ProductVariant
from apps.users.models import Store, CustomUser


class StockRecord(models.Model):
    """Current stock levels for each variant at each location"""
    
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='stock_records'
    )
    location = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='stock_records'
    )
    quantity = models.IntegerField(default=0, help_text="Total quantity in stock")
    reserved_quantity = models.IntegerField(
        default=0,
        help_text="Quantity reserved for pending orders"
    )
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('variant', 'location')
        ordering = ['variant', 'location']
    
    def __str__(self):
        return f"{self.variant.sku} @ {self.location.name}: {self.available_quantity}"
    
    @property
    def available_quantity(self):
        """Quantity available for new orders"""
        return max(0, self.quantity - self.reserved_quantity)
    
    def reserve_stock(self, qty):
        """Reserve stock for pending order"""
        if self.available_quantity >= qty:
            self.reserved_quantity += qty
            self.save()
            return True
        return False
    
    def release_reservation(self, qty):
        """Release reserved stock (cancelled order)"""
        self.reserved_quantity = max(0, self.reserved_quantity - qty)
        self.save()
    
    def confirm_sale(self, qty):
        """Confirm sale - decrement both quantity and reserved"""
        self.quantity = max(0, self.quantity - qty)
        self.reserved_quantity = max(0, self.reserved_quantity - qty)
        self.save()


class StockTransaction(models.Model):
    """Audit trail for all stock movements"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('TRANSFER', 'Transfer'),
        ('ADJUSTMENT', 'Manual Adjustment'),
        ('RETURN', 'Return'),
    ]
    
    REFERENCE_TYPE_CHOICES = [
        ('PO', 'Purchase Order'),
        ('SO', 'Sales Order'),
        ('TRANSFER', 'Stock Transfer'),
        ('RETURN', 'Return'),
        ('ADJUSTMENT', 'Manual Adjustment'),
    ]
    
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='stock_transactions'
    )
    location = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='stock_transactions'
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    quantity = models.IntegerField(help_text="Positive for IN, negative for OUT")
    reference_type = models.CharField(max_length=20, choices=REFERENCE_TYPE_CHOICES)
    reference_id = models.IntegerField(help_text="ID of the related record")
    performed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='stock_transactions'
    )
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.transaction_type} - {self.variant.sku} @ {self.location.name}: {self.quantity}"


class StockAlert(models.Model):
    """Low stock alerts configuration"""
    
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='stock_alerts'
    )
    location = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='stock_alerts'
    )
    threshold = models.PositiveIntegerField(
        default=10,
        help_text="Alert when stock falls below this level"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('variant', 'location')
        ordering = ['variant', 'location']
    
    def __str__(self):
        return f"Alert: {self.variant.sku} @ {self.location.name} (threshold: {self.threshold})"
    
    def check_alert(self):
        """Check if current stock is below threshold"""
        try:
            stock = StockRecord.objects.get(variant=self.variant, location=self.location)
            return stock.available_quantity < self.threshold
        except StockRecord.DoesNotExist:
            return True  # No stock record = alert needed
