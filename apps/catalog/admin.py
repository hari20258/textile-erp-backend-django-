from django.contrib import admin
from .models import Category, Product, ProductVariant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'is_active', 'created_at')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('sku', 'size', 'color', 'fabric_type', 'retail_price', 'wholesale_price', 'min_wholesale_qty', 'is_active')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'base_price', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'brand')
    search_fields = ('name', 'description')
    inlines = [ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('sku', 'product', 'size', 'color', 'fabric_type', 'retail_price', 'wholesale_price', 'is_active')
    list_filter = ('is_active', 'size', 'color', 'fabric_type', 'product__category')
    search_fields = ('sku', 'product__name', 'color', 'fabric_type')
