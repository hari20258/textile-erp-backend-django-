from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'store_type', 'is_active', 'created_at')
    list_filter = ('store_type', 'is_active')
    search_fields = ('name', 'code', 'address')


@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'store', 'is_approved', 'is_active')
    list_filter = ('role', 'is_approved', 'is_active', 'store')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'phone', 'store', 'is_approved', 'address')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'phone', 'store', 'is_approved', 'address')
        }),
    )
