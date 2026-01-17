from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Order, Invoice, Payment
from .serializers import OrderSerializer, InvoiceSerializer, PaymentSerializer
from apps.users.permissions import IsSalesStaff, IsCustomer

class OrderViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for sales orders
    Create: Sales staff, managers, admins, AND approved customers
    View own orders: Customers
    View all: Sales staff, managers, admins
    """
    queryset = Order.objects.all().select_related(
        'customer', 'store', 'created_by'
    ).prefetch_related('items__variant')
    serializer_class = OrderSerializer
    filterset_fields = ['customer', 'store', 'order_type', 'status', 'payment_status']
    search_fields = ['order_number', 'customer__username']
    ordering_fields = ['order_date', 'total_amount', 'created_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """
        Permissions:
        - Create: Staff OR Approved Customers
        - Update/Delete: Staff only
        - List/Retrieve: Authenticated (filtered by queryset)
        """
        if self.action == 'create':
            return [(IsSalesStaff | IsCustomer)()]
        # Allow customers to delete their own pending orders
        if self.action == 'destroy':
             return [(IsSalesStaff | IsCustomer)()]
        if self.action in ['update', 'partial_update']:
            return [IsSalesStaff()]
        
        # List/Retrieve: Strict access control
        return [(IsSalesStaff | IsCustomer)()]

    @transaction.atomic
    def perform_destroy(self, instance):
        """Release stock reservation when order is deleted"""
        from apps.inventory.models import StockRecord
        
        if instance.status not in ['PENDING', 'CANCELLED']:
            # Prevent deleting confirmed orders to maintain audit trail
            # (In a real app, this should return 400, but perform_destroy returns None. 
            # Ideally permissions or destroy() override handles this, but this is a safe guard)
            raise ValueError("Only PENDING or CANCELLED orders can be deleted")

        # Release reservations if PENDING
        if instance.status == 'PENDING':
            for item in instance.items.all():
                try:
                    stock = StockRecord.objects.select_for_update().get(
                        variant=item.variant,
                        location=instance.store
                    )
                    stock.reserved_quantity = max(0, stock.reserved_quantity - item.quantity)
                    stock.save()
                except StockRecord.DoesNotExist:
                    pass
        
        instance.delete()
    
    def get_queryset(self):
        """Filter orders based on user role"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Staff can see all, Customers can see own
        if user.role in ['ADMIN', 'STORE_MANAGER', 'SALES_STAFF']:
            return queryset
        elif user.role == 'CUSTOMER':
            return queryset.filter(customer=user)
            
        # Suppliers and others see nothing
        return queryset.none()
    
    @action(detail=True, methods=['post'], permission_classes=[IsSalesStaff])
    @transaction.atomic
    def confirm(self, request, pk=None):
        """
        Confirm order - decrement stock, release reservation
        """
        from apps.inventory.models import StockRecord, StockTransaction
        
        order = self.get_object()
        
        if order.status != 'PENDING':
            return Response(
                {'error': 'Only PENDING orders can be confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process each item: decrement quantity, release reservation
        for item in order.items.all():
            stock = StockRecord.objects.select_for_update().get(
                variant=item.variant,
                location=order.store
            )
            
            # Decrement actual quantity
            stock.quantity -= item.quantity
            # Release reservation
            stock.reserved_quantity -= item.quantity
            stock.save()
            
            #Create stock transaction for sale
            StockTransaction.objects.create(
                variant=item.variant,
                location=order.store,
                transaction_type='OUT',
                quantity=-item.quantity,
                reference_type='SO',
                reference_id=order.id,
                performed_by=request.user,
                notes=f"Order #{order.order_number} confirmed"
            )
        
        # Update order status
        order.status = 'CONFIRMED'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsSalesStaff | IsCustomer])
    @transaction.atomic
    def cancel(self, request, pk=None):
        """
        Cancel order - release stock reservations
        """
        from apps.inventory.models import StockRecord
        
        order = self.get_object()
        
        if order.status not in ['PENDING', 'CONFIRMED']:
            return Response(
                {'error': 'Only PENDING or CONFIRMED orders can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Release stock reservations
        for item in order.items.all():
            stock = StockRecord.objects.select_for_update().get(
                variant=item.variant,
                location=order.store
            )
            
            if order.status == 'PENDING':
                # Just release reservation
                stock.reserved_quantity -= item.quantity
            else:  # CONFIRMED
                # Add back to quantity and release reservation
                stock.quantity += item.quantity
                stock.reserved_quantity -= item.quantity
            
            stock.save()
        
        # Update order status
        order.status = 'CANCELLED'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsSalesStaff])
    def mark_shipped(self, request, pk=None):
        """Mark order as shipped"""
        order = self.get_object()
        
        if order.status != 'CONFIRMED':
            return Response(
                {'error': 'Only CONFIRMED orders can be shipped'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'SHIPPED'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsSalesStaff])
    def mark_delivered(self, request, pk=None):
        """Mark order as delivered"""
        order = self.get_object()
        
        if order.status != 'SHIPPED':
            return Response(
                {'error': 'Only SHIPPED orders can be delivered'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'DELIVERED'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)


class InvoiceViewSet(viewsets.ModelViewSet):
    """
Fixed operations for invoices
    Automatically created for confirmed orders
    """
    queryset = Invoice.objects.all().select_related('order__customer')
    serializer_class = InvoiceSerializer
    permission_classes = [IsSalesStaff]
    filterset_fields = ['order']
    search_fields = ['invoice_number', 'order__order_number']
    ordering_fields = ['invoice_date', 'due_date', 'amount']
    ordering = ['-invoice_date']


class PaymentViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for payments
    Recording payment updates invoice and order payment status
    """
    queryset = Payment.objects.all().select_related('invoice__order')
    serializer_class = PaymentSerializer
    permission_classes = [IsSalesStaff]
    filterset_fields = ['invoice', 'payment_method']
    search_fields = ['invoice__invoice_number', 'reference_number']
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']
