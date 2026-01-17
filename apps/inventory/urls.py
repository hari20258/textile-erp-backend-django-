from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StockRecordViewSet,
    StockTransactionViewSet,
    StockAdjustmentView,
    StockAlertViewSet
)

router = DefaultRouter()
router.register(r'stock', StockRecordViewSet, basename='stock-record')
router.register(r'transactions', StockTransactionViewSet, basename='stock-transaction')
router.register(r'alerts', StockAlertViewSet, basename='stock-alert')

urlpatterns = [
    path('adjust/', StockAdjustmentView.as_view(), name='stock-adjust'),
    path('', include(router.urls)),
]
