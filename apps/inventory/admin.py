from django.contrib import admin
from .models import StockRecord, StockTransaction, StockAlert


@admin.register(StockRecord)
class StockRecordAdmin(admin.ModelAdmin):
    list_display = ('variant', 'location', 'quantity', 'reserved_quantity', 'available_quantity', 'last_updated')
    list_filter = ('location',)
    search_fields = ('variant__sku', 'variant__product__name', 'location__name')
    readonly_fields = ('last_updated',)


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('variant', 'location', 'transaction_type', 'quantity', 'reference_type', 'reference_id', 'timestamp')
    list_filter = ('transaction_type', 'reference_type', 'location', 'timestamp')
    search_fields = ('variant__sku', 'variant__product__name', 'notes')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ('variant', 'location', 'threshold', 'is_active', 'current_stock_status')
    list_filter = ('is_active', 'location')
    search_fields = ('variant__sku', 'variant__product__name')
    
    def current_stock_status(self, obj):
        if obj.check_alert():
            return "⚠️ Below threshold"
        return "✓ OK"
    current_stock_status.short_description = "Status"
