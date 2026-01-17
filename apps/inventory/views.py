from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import StockRecord, StockTransaction, StockAlert
from .serializers import (
    StockRecordSerializer,
    StockTransactionSerializer,
    StockAdjustmentSerializer,
    StockAlertSerializer
)
from apps.users.permissions import IsStoreManager, IsSalesStaff


class StockRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for stock records
    List and retrieve current stock levels
    """
    queryset = StockRecord.objects.all().select_related('variant', 'location')
    serializer_class = StockRecordSerializer
    permission_classes = [IsSalesStaff]
    filterset_fields = ['variant', 'location']
    search_fields = ['variant__sku', 'variant__product__name', 'location__name']
    ordering_fields = ['quantity', 'available_quantity', 'last_updated']
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get all stock records with low available quantity"""
        threshold = request.query_params.get('threshold', 10)
        low_stock = self.queryset.filter(quantity__lte=threshold)
        serializer = self.get_serializer(low_stock, many=True)
        return Response(serializer.data)


class StockTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for stock transaction history
    Provides audit trail of all stock movements
    """
    queryset = StockTransaction.objects.all().select_related(
        'variant', 'location', 'performed_by'
    )
    serializer_class = StockTransactionSerializer
    permission_classes = [IsSalesStaff]
    filterset_fields = ['variant', 'location', 'transaction_type', 'reference_type']
    search_fields = ['variant__sku', 'notes']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']


class StockAdjustmentView(generics.CreateAPIView):
    """
    Create manual stock adjustments
    Only accessible to store managers and admins
    """
    serializer_class = StockAdjustmentSerializer
    permission_classes = [IsStoreManager]
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        variant = serializer.validated_data['variant_obj']
        location = serializer.validated_data['location_obj']
        adjustment = serializer.validated_data['adjustment']
        reason = serializer.validated_data['reason']
        
        # Get or create stock record with locking
        stock, created = StockRecord.objects.select_for_update().get_or_create(
            variant=variant,
            location=location,
            defaults={'quantity': 0, 'reserved_quantity': 0}
        )
        
        # Update quantity
        stock.quantity += adjustment
        stock.save()
        
        # Create transaction record
        StockTransaction.objects.create(
            variant=variant,
            location=location,
            transaction_type='ADJUSTMENT',
            quantity=adjustment,
            reference_type='ADJUSTMENT',
            reference_id=stock.id,
            performed_by=request.user,
            notes=reason
        )
        
        # Return updated stock record
        stock_serializer = StockRecordSerializer(stock)
        return Response(stock_serializer.data, status=status.HTTP_201_CREATED)


class StockAlertViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for stock alerts
    Managers can configure low-stock thresholds
    """
    queryset = StockAlert.objects.all().select_related('variant', 'location')
    serializer_class = StockAlertSerializer
    permission_classes = [IsStoreManager]
    filterset_fields = ['variant', 'location', 'is_active']
    
    @action(detail=False, methods=['get'])
    def triggered(self, request):
        """Get all alerts that are currently triggered (below threshold)"""
        active_alerts = self.queryset.filter(is_active=True)
        triggered = [alert for alert in active_alerts if alert.check_alert()]
        serializer = self.get_serializer(triggered, many=True)
        return Response(serializer.data)
