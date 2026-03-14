from django.contrib import admin
from .models import StockLedger

@admin.register(StockLedger)
class StockLedgerAdmin(admin.ModelAdmin):
    list_display  = ['reference', 'product', 'move_type',
                     'quantity', 'stock_before', 'stock_after', 'created_at']
    list_filter   = ['move_type']
    search_fields = ['reference', 'product__name']
    readonly_fields = ['created_at']