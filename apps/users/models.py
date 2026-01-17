from django.contrib.auth.models import AbstractUser
from django.db import models


class Store(models.Model):
    """Store or warehouse location model"""
    
    STORE_TYPE_CHOICES = [
        ('RETAIL', 'Retail Store'),
        ('WAREHOUSE', 'Warehouse'),
    ]
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    store_type = models.CharField(max_length=20, choices=STORE_TYPE_CHOICES, default='RETAIL')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.code})"


class CustomUser(AbstractUser):
    """Custom user model with role-based access"""
    
    ROLE_CHOICES = [
        ('ADMIN', 'Admin / Owner'),
        ('STORE_MANAGER', 'Store Manager'),
        ('SALES_STAFF', 'Sales Staff'),
        ('SUPPLIER', 'Supplier'),
        ('CUSTOMER', 'Customer / Wholesale Buyer'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    phone = models.CharField(max_length=20, blank=True)
    store = models.ForeignKey(
        Store, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Assigned store for staff members"
    )
    is_approved = models.BooleanField(
        default=False,
        help_text="For suppliers and wholesale customers - requires admin approval"
    )
    address = models.TextField(blank=True)
    
    class Meta:
        ordering = ['username']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def save(self, *args, **kwargs):
        # Auto-approve admins, managers, and sales staff
        if self.role in ['ADMIN', 'STORE_MANAGER', 'SALES_STAFF']:
            self.is_approved = True
        super().save(*args, **kwargs)
