from rest_framework import serializers
from django.db import models as django_models
from .models import StockRecord, StockTransaction, StockAlert
from apps.catalog.serializers import ProductVariantSerializer
from apps.users.serializers import StoreSerializer


class StockRecordSerializer(serializers.ModelSerializer):
    """Serializer for stock records"""
    
    variant_details = ProductVariantSerializer(source='variant', read_only=True)
    location_details = StoreSerializer(source='location', read_only=True)
    available_quantity = serializers.IntegerField(read_only=True)
    
    details_url = serializers.SerializerMethodField()
    
    class Meta:
        model = StockRecord
        fields = [
            'id', 'variant', 'variant_details', 'location', 'location_details',
            'quantity', 'reserved_quantity', 'available_quantity', 'details_url', 'last_updated'
        ]
        read_only_fields = ['last_updated', 'reserved_quantity']
        
    def get_details_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/inventory/stock/{obj.id}/')
        return None


class StockTransactionSerializer(serializers.ModelSerializer):
    """Serializer for stock transaction history"""
    
    variant_sku = serializers.CharField(source='variant.sku', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.username', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = StockTransaction
        fields = [
            'id', 'variant', 'variant_sku', 'location', 'location_name',
            'transaction_type', 'transaction_type_display', 'quantity',
            'reference_type', 'reference_id', 'performed_by', 'performed_by_name',
            'notes', 'timestamp'
        ]
        read_only_fields = ['timestamp']


class StockAdjustmentSerializer(serializers.Serializer):
    """Serializer for manual stock adjustments"""
    
    variant = serializers.IntegerField()
    location = serializers.IntegerField(required=False)
    adjustment = serializers.IntegerField(help_text="Positive to add, negative to remove")
    reason = serializers.CharField(max_length=500)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.store:
            # Store managers can only adjust their own store
            self.fields['location'].read_only = True
    
    def validate_adjustment(self, value):
        if value == 0:
            raise serializers.ValidationError("Adjustment cannot be zero")
        return value
    
    def validate(self, data):
        """Validate that variant and location exist and have stock record"""
        from apps.catalog.models import ProductVariant
        from apps.users.models import Store
        
        try:
            variant = ProductVariant.objects.get(id=data['variant'])
        except ProductVariant.DoesNotExist:
            raise serializers.ValidationError({"variant": "Product variant not found"})
        
        # Auto-assign location for store managers
        request = self.context.get('request')
        if request and request.user.store:
            location = request.user.store
        else:
            try:
                location = Store.objects.get(id=data['location'])
            except Store.DoesNotExist:
                raise serializers.ValidationError({"location": "Store location not found"})
        
        # Check if negative adjustment would result in negative stock
        if data['adjustment'] < 0:
            try:
                stock = StockRecord.objects.get(variant=variant, location=location)
                if stock.quantity + data['adjustment'] < 0:
                    raise serializers.ValidationError({
                        "adjustment": f"Cannot remove {abs(data['adjustment'])} units. Only {stock.quantity} available."
                    })
            except StockRecord.DoesNotExist:
                raise serializers.ValidationError({
                    "adjustment": "No stock record exists for this variant and location"
                })
        
        data['variant_obj'] = variant
        data['location_obj'] = location
        return data


class StockAlertSerializer(serializers.ModelSerializer):
    """Serializer for low stock alerts"""
    
    variant_details = ProductVariantSerializer(source='variant', read_only=True)
    location_details = StoreSerializer(source='location', read_only=True)
    current_stock = serializers.SerializerMethodField()
    is_below_threshold = serializers.SerializerMethodField()
    
    class Meta:
        model = StockAlert
        fields = [
            'id', 'variant', 'variant_details', 'location', 'location_details',
            'threshold', 'is_active', 'current_stock', 'is_below_threshold', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_current_stock(self, obj):
        """Get current available stock for this variant/location"""
        try:
            stock = StockRecord.objects.get(variant=obj.variant, location=obj.location)
            return stock.available_quantity
        except StockRecord.DoesNotExist:
            return 0
    
    def get_is_below_threshold(self, obj):
        """Check if currently below threshold"""
        return obj.check_alert()
