from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, ProductVariant
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductListSerializer,
    ProductVariantSerializer
)
from apps.core.mixins import StoreManagerModificationMixin


class CategoryViewSet(StoreManagerModificationMixin, viewsets.ModelViewSet):
    """
    CRUD operations for product categories
    Read: All authenticated users
    Create/Update/Delete: Store managers and admins only
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ProductViewSet(StoreManagerModificationMixin, viewsets.ModelViewSet):
    """
    CRUD operations for products
    List/Retrieve: All authenticated users
    Create/Update/Delete: Store managers and admins only
    """
    queryset = Product.objects.filter(is_active=True).select_related('category')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'is_active']
    search_fields = ['name', 'description', 'brand']
    ordering_fields = ['name', 'base_price', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        # Use lightweight serializer for list view
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer


class ProductVariantViewSet(StoreManagerModificationMixin, viewsets.ModelViewSet):
    """
    CRUD operations for product variants (SKU level)
    List/Retrieve: All authenticated users
    Create/Update/Delete: Store managers and admins only
    
    Supports filtering by size, color, fabric, price range, and SKU search
    """
    queryset = ProductVariant.objects.filter(is_active=True).select_related('product')
    serializer_class = ProductVariantSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'size', 'color', 'fabric_type', 'is_active']
    search_fields = ['sku', 'product__name', 'color', 'fabric_type']
    ordering_fields = ['sku', 'retail_price', 'wholesale_price', 'created_at']
    ordering = ['product', 'sku']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Price range filtering
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(retail_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(retail_price__lte=max_price)
        
        return queryset
