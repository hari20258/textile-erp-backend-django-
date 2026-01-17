from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Supplier, PurchaseOrder, GoodsReceiptNote
from .serializers import (
    SupplierSerializer,
    PurchaseOrderSerializer,
    GRNSerializer
)
from apps.users.permissions import IsStoreManager, IsSupplier


class SupplierViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for suppliers
    Accessible to managers and admins
    """
    queryset = Supplier.objects.all().select_related('user')
    serializer_class = SupplierSerializer
    permission_classes = [IsStoreManager]
    filterset_fields = ['is_active']
    search_fields = ['company_name', 'contact_person', 'email']
    ordering_fields = ['company_name', 'created_at']


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for purchase orders
    Create/Update: Managers only
    View: Managers and assigned suppliers
    """
    queryset = PurchaseOrder.objects.all().select_related(
        'supplier', 'store', 'created_by'
    ).prefetch_related('items__variant')
    serializer_class = PurchaseOrderSerializer
    filterset_fields = ['supplier', 'store', 'status']
    search_fields = ['po_number']
    ordering_fields = ['order_date', 'expected_delivery', 'created_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Managers can create/update, suppliers can view their own"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsStoreManager()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter POs based on user role"""
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.role == 'ADMIN':
            return queryset
            
        # Suppliers can only see their own POs
        if user.role == 'SUPPLIER':
            try:
                supplier = user.supplier_profile
                return queryset.filter(supplier=supplier)
            except:
                return queryset.none()
        
        # Store Managers can only see POs for their store
        if user.role == 'STORE_MANAGER' and user.store:
            return queryset.filter(store=user.store)
            
        # Everyone else (Customers, Sales Staff) sees nothing
        return queryset.none()
    
    @action(detail=True, methods=['post'], permission_classes=[IsStoreManager])
    def send_to_supplier(self, request, pk=None):
        """Mark PO as sent to supplier"""
        po = self.get_object()
        if po.status != 'DRAFT':
            return Response(
                {'error': 'Only DRAFT POs can be sent'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        po.status = 'SENT'
        po.save()
        serializer = self.get_serializer(po)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsSupplier])
    def confirm(self, request, pk=None):
        """Supplier confirms the PO"""
        po = self.get_object()
        
        # Check supplier owns this PO
        if po.supplier.user != request.user:
            return Response(
                {'error': 'You can only confirm your own POs'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if po.status != 'SENT':
            return Response(
                {'error': 'Only SENT POs can be confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        po.status = 'CONFIRMED'
        po.save()
        serializer = self.get_serializer(po)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsSupplier])
    def mark_shipped(self, request, pk=None):
        """Supplier marks PO as shipped"""
        po = self.get_object()
        
        if po.supplier.user != request.user:
            return Response(
                {'error': 'You can only update your own POs'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if po.status != 'CONFIRMED':
            return Response(
                {'error': 'Only CONFIRMED POs can be shipped'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        po.status = 'SHIPPED'
        po.save()
        serializer = self.get_serializer(po)
        return Response(serializer.data)


class GRNViewSet(viewsets.ModelViewSet):
    """
    CRUD for Goods Receipt Notes
    Create triggers atomic stock increment
    Only managers can create GRNs
    """
    queryset = GoodsReceiptNote.objects.all().select_related(
        'purchase_order', 'received_by'
    ).prefetch_related('items__po_item__variant')
    serializer_class = GRNSerializer
    permission_classes = [IsStoreManager]
    filterset_fields = ['purchase_order']
    search_fields = ['grn_number', 'purchase_order__po_number']
    ordering_fields = ['received_date', 'created_at']
    ordering = ['-created_at']
    
    def create(self, request, *args, **kwargs):
        """Create GRN with atomic stock increment"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check PO status
        po = serializer.validated_data['purchase_order']
        if po.status not in ['CONFIRMED', 'SHIPPED']:
            return Response(
                {'error': 'PO must be CONFIRMED or SHIPPED to receive goods'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create GRN (stock increment happens in serializer)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
