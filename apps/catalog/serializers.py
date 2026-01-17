from rest_framework import serializers
from django.db import models as django_models
from .models import Category, Product, ProductVariant


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories"""
    
    subcategories = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'subcategories', 'product_count', 'is_active', 'created_at']
        read_only_fields = ['slug', 'created_at']
    
    def get_subcategories(self, obj):
        # Get immediate children only (not recursive to avoid performance issues)
        subcats = obj.subcategories.filter(is_active=True)
        return [{
            'id': cat.id,
            'name': cat.name,
            'slug': cat.slug
        } for cat in subcats]
    
    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for product variants"""
    
    size_display = serializers.CharField(source='get_size_display', read_only=True)
    stock_available = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'sku', 'size', 'size_display', 'color', 'fabric_type',
            'retail_price', 'wholesale_price', 'min_wholesale_qty',
            'weight', 'stock_available', 'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_stock_available(self, obj):
        """Check if variant has available stock across all locations"""
        try:
            from apps.inventory.models import StockRecord
            total_stock = StockRecord.objects.filter(variant=obj).aggregate(
                total=django_models.Sum('quantity')
            )['total'] or 0
            return total_stock > 0
        except:
            # Return None if inventory app not yet set up
            return None
    
    def validate(self, data):
        """Validate pricing and wholesale quantity"""
        wholesale_price = data.get('wholesale_price')
        retail_price = data.get('retail_price')
        min_qty = data.get('min_wholesale_qty')
        
        if wholesale_price and retail_price and wholesale_price >= retail_price:
            raise serializers.ValidationError(
                "Wholesale price must be less than retail price"
            )
        
        if min_qty and min_qty < 1:
            raise serializers.ValidationError(
                "Minimum wholesale quantity must be at least 1"
            )
        
        return data


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products with nested variants"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    variant_count = serializers.SerializerMethodField()
    details_url = serializers.SerializerMethodField()
    variants_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'category_name', 'brand',
            'base_price', 'variants', 'variant_count', 'details_url', 'variants_url',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_details_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/catalog/products/{obj.id}/')
        return None
    
    def get_variants_url(self, obj):
        request = self.context.get('request')
        if request:
            # Link to the variants list filtered by this product
            return request.build_absolute_uri(f'/api/catalog/variants/?product={obj.id}')
        return None
    
    def get_variant_count(self, obj):
        return obj.variants.filter(is_active=True).count()


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listing (without variants)"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    variant_count = serializers.SerializerMethodField()
    price_range = serializers.SerializerMethodField()
    details_url = serializers.SerializerMethodField()
    variants_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_name', 'brand',
            'base_price', 'variant_count', 'price_range', 'details_url', 'variants_url',
            'is_active', 'created_at'
        ]
    
    def get_details_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/catalog/products/{obj.id}/')
        return None

    def get_variants_url(self, obj):
        request = self.context.get('request')
        if request:
            # Link to the variants list filtered by this product
            return request.build_absolute_uri(f'/api/catalog/variants/?product={obj.id}')
        return None
    
    def get_variant_count(self, obj):
        return obj.variants.filter(is_active=True).count()
    
    def get_price_range(self, obj):
        """Get min and max retail prices from variants"""
        variants = obj.variants.filter(is_active=True)
        if not variants.exists():
            return None
        
        prices = variants.values_list('retail_price', flat=True)
        return {
            'min': min(prices),
            'max': max(prices)
        }
