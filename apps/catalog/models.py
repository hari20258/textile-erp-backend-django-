from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Product category with hierarchical structure"""
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Main product model"""
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )
    brand = models.CharField(max_length=100, blank=True)
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Base/reference price for the product"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    """Product variant (SKU level) with size, color, fabric variations"""
    
    SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', '2X Large'),
        ('CUSTOM', 'Custom Size'),
    ]
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    sku = models.CharField(max_length=100, unique=True, help_text="Stock Keeping Unit")
    
    # Variant attributes
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, blank=True)
    color = models.CharField(max_length=50, blank=True)
    fabric_type = models.CharField(max_length=100, blank=True, help_text="e.g., Cotton, Silk, Polyester")
    
    # Pricing
    retail_price = models.DecimalField(max_digits=10, decimal_places=2)
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_wholesale_qty = models.PositiveIntegerField(
        default=10,
        help_text="Minimum quantity for wholesale pricing"
    )
    
    # Additional info
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight in kg"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['product', 'sku']
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'
    
    def __str__(self):
        return f"{self.product.name} - {self.sku}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.wholesale_price >= self.retail_price:
            raise ValidationError("Wholesale price must be less than retail price")
        if self.min_wholesale_qty < 1:
            raise ValidationError("Minimum wholesale quantity must be at least 1")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
