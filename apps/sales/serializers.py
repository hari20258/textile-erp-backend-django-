from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem, Invoice, Payment
from apps.catalog.serializers import ProductVariantSerializer
from django.contrib.auth import get_user_model
from apps.users.serializers import StoreSerializer

User = get_user_model()


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order line items"""
    
    variant_details = ProductVariantSerializer(source='variant', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'variant', 'variant_details', 'quantity', 'unit_price', 'line_total']
        read_only_fields = ['line_total', 'unit_price']
    
    def validate(self, data):
        """Validate wholesale minimum quantity"""
        variant = data.get('variant')
        quantity = data.get('quantity')
        
        # Get order type from parent serializer context
        order_type = self.context.get('order_type')
        
        if order_type == 'WHOLESALE' and variant:
            if quantity < variant.min_wholesale_qty:
                raise serializers.ValidationError({
                    'quantity': f'Minimum wholesale quantity is {variant.min_wholesale_qty}'
                })
        
        return data


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for sales orders with stock reservation"""
    
from apps.catalog.models import ProductVariant

from apps.core.mixins import QuickAddValidationMixin

class OrderSerializer(QuickAddValidationMixin, serializers.ModelSerializer):
    """Serializer for sales orders with stock reservation"""
    
    # Filter customer dropdown to only show CUSTOMER role users
    customer = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='CUSTOMER'),
        required=False  # Optional because it's auto-assigned for customers
    )

    # Standard nested items (for JSON usage)
    items = OrderItemSerializer(many=True, required=False)
    
    # Demo Helpers: Simple fields for HTML Form (Write Only)
    # This allows picking 1 item from a dropdown instead of writing JSON
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
        initial=1,
        label="Quantity (HTML Form)"
    )

    customer_details = serializers.SerializerMethodField()
    store_details = StoreSerializer(source='store', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_type_display = serializers.CharField(source='get_order_type_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)

    def validate(self, attrs):
        """Allow creating order via HTML form (Quick Add) or JSON (Items list)"""
        # Use Mixin to handle logic
        return self.validate_quick_add(attrs)
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request.user, 'role') and request.user.role == 'CUSTOMER':
            # Customers cannot choose the customer field - it's auto-assigned to them
            self.fields['customer'].read_only = True
            
            # Customers cannot set these fields
            restricted_fields = ['discount', 'payment_status', 'delivery_date', 'status', 'order_type']
            for field in restricted_fields:
                if field in self.fields:
                    self.fields[field].read_only = True
        
        # Enforce store restriction for Managers/Staff
        if request and request.user.store:
            # If user belongs to a store, they can ONLY order for that store
            self.fields['store'].read_only = True

    def get_customer_details(self, obj):
        return {
            'id': obj.customer.id,
            'username': obj.customer.username,
            'email': obj.customer.email,
            'phone': obj.customer.phone
        }
    
    confirm_url = serializers.SerializerMethodField()
    cancel_url = serializers.SerializerMethodField()
    details_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'customer_details', 'order_type', 'order_type_display',
            'status', 'status_display', 'order_date', 'delivery_date',
            'store', 'store_details', 'subtotal', 'discount', 'total_amount',
            'payment_status', 'payment_status_display', 'items', 
            'quick_variant', 'quick_quantity',
            'confirm_url', 'cancel_url', 'details_url',
            'created_by', 'created_by_name', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'order_number', 'order_date', 'subtotal', 'total_amount',
            'created_at', 'updated_at', 'created_by'
        ]
        
    def get_details_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/sales/orders/{obj.id}/')
        return None

    def get_confirm_url(self, obj):
        request = self.context.get('request')
        if request and obj.status == 'PENDING':
            return request.build_absolute_uri(f'/api/sales/orders/{obj.id}/confirm/')
        return None

    def get_cancel_url(self, obj):
        request = self.context.get('request')
        if request and obj.status not in ['CANCELLED', 'DELIVERED']:
            return request.build_absolute_uri(f'/api/sales/orders/{obj.id}/cancel/')
        return None

    @transaction.atomic
    def create(self, validated_data):
        from apps.inventory.models import StockRecord, StockTransaction
        
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        
        # Auto-assign customer if not provided (for customer role)
        if 'customer' not in validated_data and user.role == 'CUSTOMER':
            validated_data['customer'] = user
            
        validated_data['created_by'] = user
        order_type = validated_data.get('order_type', 'RETAIL')
        
        # Auto-assign store if user is restricted to one
        if user.store:
            validated_data['store'] = user.store
            
        store = validated_data['store']
        
        
        # Check stock availability first
        for item_data in items_data:
            variant = item_data['variant']
            quantity = item_data['quantity']
            
            try:
                stock = StockRecord.objects.select_for_update().get(
                    variant=variant,
                    location=store
                )
                if stock.available_quantity < quantity:
                    raise serializers.ValidationError({
                        'items': f'Insufficient stock for {variant.sku}. Available: {stock.available_quantity}'
                    })
            except StockRecord.DoesNotExist:
                raise serializers.ValidationError({
                    'items': f'No stock available for {variant.sku} at {store.name}'
                })
        
        # Create order
        order = Order.objects.create(**validated_data)
        
        # Create items, reserve stock, and calculate totals
        subtotal = 0
        for item_data in items_data:
            variant = item_data['variant']
            quantity = item_data['quantity']
            
            # Set price based on order type
            if order_type == 'WHOLESALE':
                price = variant.wholesale_price
            else:
                price = variant.retail_price
            
            item_data['unit_price'] = price
            item = OrderItem.objects.create(order=order, **item_data)
            subtotal += item.line_total
            
            # Reserve stock
            stock = StockRecord.objects.select_for_update().get(
                variant=variant,
                location=store
            )
            stock.reserved_quantity += quantity
            stock.save()
            
            # Create transaction for reservation
            StockTransaction.objects.create(
                variant=variant,
                location=store,
                transaction_type='OUT',
                quantity=-quantity,  # Negative for reservation
                reference_type='SO',
                reference_id=order.id,
                performed_by=self.context['request'].user,
                notes=f"Reserved for Order #{order.order_number}"
            )
        
        # Update order totals
        order.subtotal = subtotal
        order.total_amount = subtotal - order.discount
        order.save()
        
        return order
    
    def get_serializer_context(self):
        """Pass order type to item serializers"""
        context = super().get_serializer_context()
        if self.instance:
            context['order_type'] = self.instance.order_type
        return context


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for invoices"""
    
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    customer_name = serializers.CharField(source='order.customer.username', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'order', 'order_number', 'customer_name',
            'invoice_date', 'due_date', 'amount', 'paid_amount', 'balance', 'created_at'
        ]
        read_only_fields = ['invoice_number', 'invoice_date', 'balance', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments"""
    
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'invoice_number', 'payment_date', 'amount',
            'payment_method', 'payment_method_display', 'reference_number', 'notes'
        ]
        read_only_fields = ['payment_date']
    
    @transaction.atomic
    def create(self, validated_data):
        invoice = validated_data['invoice']
        amount = validated_data['amount']
        
        # Validate amount
        if amount > invoice.balance:
            raise serializers.ValidationError({
                'amount': f'Payment amount cannot exceed balance of {invoice.balance}'
            })
        
        # Create payment
        payment = Payment.objects.create(**validated_data)
        
        # Update invoice
        invoice.paid_amount += amount
        invoice.save()
        
        # Update order payment status
        order = invoice.order
        if invoice.balance == 0:
            order.payment_status = 'PAID'
        else:
            order.payment_status = 'PARTIAL'
        order.save()
        
        return payment
