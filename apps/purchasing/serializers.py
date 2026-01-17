from rest_framework import serializers
from django.db import transaction
from .models import Supplier, PurchaseOrder, PurchaseOrderItem, GoodsReceiptNote, GRNItem
from apps.catalog.models import ProductVariant
from apps.catalog.serializers import ProductVariantSerializer
from apps.users.serializers import StoreSerializer


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for supplier management"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'user', 'username', 'company_name', 'contact_person',
            'phone', 'email', 'address', 'tax_id', 'payment_terms',
            'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for PO line items"""
    
    variant_details = ProductVariantSerializer(source='variant', read_only=True)
    
    class Meta:
        model = PurchaseOrderItem
        fields = ['id', 'variant', 'variant_details', 'quantity', 'unit_price', 'line_total']
        read_only_fields = ['line_total']


from apps.core.mixins import QuickAddValidationMixin

class PurchaseOrderSerializer(QuickAddValidationMixin, serializers.ModelSerializer):
    """Serializer for purchase orders"""
    
    items = PurchaseOrderItemSerializer(many=True, required=False)
    supplier_details = SupplierSerializer(source='supplier', read_only=True)
    store_details = StoreSerializer(source='store', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Quick Add Fields for HTML Form
    quick_variant = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.filter(is_active=True),
        write_only=True,
        required=False,
        label="Select Item (HTML Form)"
    )
    quick_quantity = serializers.IntegerField(
        write_only=True,
        required=False,
        min_value=1,
        initial=10,
        label="Quantity (HTML Form)"
    )
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'po_number', 'supplier', 'supplier_details', 'store', 'store_details',
            'status', 'status_display', 'order_date', 'expected_delivery',
            'total_amount', 'items', 'created_by', 'created_by_name',
            'notes', 'created_at', 'updated_at',
            'quick_variant', 'quick_quantity'
        ]
        read_only_fields = ['po_number', 'order_date', 'created_at', 'updated_at', 'total_amount', 'created_by']
    
    def validate(self, attrs):
        """Allow creating PO via HTML form (Quick Add) or JSON"""
        # Use Mixin to handle Quick Add logic
        # For POs, we default unit_price to retail_price (as a placeholder)
        return self.validate_quick_add(attrs, price_source_field='retail_price')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.store:
            # Managers can only order for their store
            self.fields['store'].read_only = True

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        validated_data['created_by'] = user
        
        # Auto-assign store for managers
        if user.store:
            validated_data['store'] = user.store
        
        # Create PO
        po = PurchaseOrder.objects.create(**validated_data)
        
        # Create items and calculate total
        total = 0
        for item_data in items_data:
            item = PurchaseOrderItem.objects.create(purchase_order=po, **item_data)
            total += item.line_total
        
        # Update total
        po.total_amount = total
        po.save()
        
        return po
    
    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        # Update PO fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update items if provided
        if items_data is not None:
            # Delete existing items
            instance.items.all().delete()
            
            # Create new items
            total = 0
            for item_data in items_data:
                item = PurchaseOrderItem.objects.create(purchase_order=instance, **item_data)
                total += item.line_total
            
            # Update total
            instance.total_amount = total
            instance.save()
        
        return instance


class GRNItemSerializer(serializers.ModelSerializer):
    """Serializer for GRN line items"""
    
    variant_sku = serializers.CharField(source='po_item.variant.sku', read_only=True)
    ordered_quantity = serializers.IntegerField(source='po_item.quantity', read_only=True)
    
    class Meta:
        model = GRNItem
        fields = [
            'id', 'po_item', 'variant_sku', 'ordered_quantity',
            'quantity_received', 'quantity_rejected', 'remarks'
        ]
    
    def validate(self, data):
        """Validate GRN quantities"""
        po_item = data.get('po_item')
        qty_received = data.get('quantity_received', 0)
        qty_rejected = data.get('quantity_rejected', 0)
        
        # Check total received doesn't exceed ordered
        total_qty = qty_received + qty_rejected
        if total_qty > po_item.quantity:
            raise serializers.ValidationError(
                f"Total quantity ({total_qty}) cannot exceed ordered quantity ({po_item.quantity})"
            )
        
        return data


class GRNSerializer(serializers.ModelSerializer):
    """Serializer for Goods Receipt Notes with atomic stock increment"""
    
    items = GRNItemSerializer(many=True, required=False)
    po_number = serializers.CharField(source='purchase_order.po_number', read_only=True)
    received_by_name = serializers.CharField(source='received_by.username', read_only=True)
    
    # Quick Receive Logic
    receive_all = serializers.BooleanField(
        write_only=True, 
        required=False, 
        default=True,
        label="Receive All (Auto-fill items from PO)"
    )
    
    class Meta:
        model = GoodsReceiptNote
        fields = [
            'id', 'grn_number', 'purchase_order', 'po_number',
            'received_date', 'received_by', 'received_by_name',
            'items', 'notes', 'created_at',
            'receive_all'
        ]
        read_only_fields = ['grn_number', 'received_date', 'received_by', 'created_at']

    def validate(self, attrs):
        """Auto-fill items if receive_all is True"""
        # If items not provided (e.g. HTML form) and receive_all is Checked
        if not attrs.get('items') and attrs.get('receive_all'):
            po = attrs.get('purchase_order')
            if po:
                items_list = []
                for po_item in po.items.all():
                    items_list.append({
                        'po_item': po_item,
                        'quantity_received': po_item.quantity, # Default to receiving full amount
                        'quantity_rejected': 0
                    })
                attrs['items'] = items_list
        
        # Determine receiving location early for validation if needed
        # (Not strictly needed here as create() handles it, but good for completeness)
        
        if not attrs.get('items'):
             raise serializers.ValidationError("You must either provide 'items' (JSON) or check 'Receive All'.")
             
        return attrs

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.store:
            # Filter dropdown to show only valid POs for this store
            self.fields['purchase_order'].queryset = PurchaseOrder.objects.filter(
                store=request.user.store,
                status__in=['CONFIRMED', 'SHIPPED']
            )
    
    @transaction.atomic
    def create(self, validated_data):
        from apps.inventory.models import StockRecord, StockTransaction
        
        items_data = validated_data.pop('items')
        # receive_all is not a model field, so we must remove it
        validated_data.pop('receive_all', None)
        
        validated_data['received_by'] = self.context['request'].user
        
        # Create GRN
        grn = GoodsReceiptNote.objects.create(**validated_data)
        po = grn.purchase_order
        receiving_location = po.store
        
        # Process each item: create GRN item and increment stock
        for item_data in items_data:
            po_item = item_data['po_item']
            qty_received = item_data['quantity_received']
            
            # Create GRN item
            grn_item = GRNItem.objects.create(grn=grn, **item_data)
            
            # Atomic stock increment
            if qty_received > 0:
                stock, created = StockRecord.objects.select_for_update().get_or_create(
                    variant=po_item.variant,
                    location=receiving_location,
                    defaults={'quantity': 0, 'reserved_quantity': 0}
                )
                
                stock.quantity += qty_received
                stock.save()
                
                # Create stock transaction
                StockTransaction.objects.create(
                    variant=po_item.variant,
                    location=receiving_location,
                    transaction_type='IN',
                    quantity=qty_received,
                    reference_type='PO',
                    reference_id=po.id,
                    performed_by=self.context['request'].user,
                    notes=f"GRN #{grn.grn_number} - PO #{po.po_number}"
                )
        
        # Update PO status to RECEIVED
        po.status = 'RECEIVED'
        po.save()
        
        return grn
