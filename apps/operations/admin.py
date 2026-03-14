from django.contrib import admin
from .models import Receipt, ReceiptItem, Delivery, DeliveryItem, Adjustment

class ReceiptItemInline(admin.TabularInline):
    model = ReceiptItem
    extra = 1

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display  = ['reference', 'supplier', 'status', 'created_at']
    list_filter   = ['status']
    inlines       = [ReceiptItemInline]

class DeliveryItemInline(admin.TabularInline):
    model = DeliveryItem
    extra = 1

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display  = ['reference', 'status', 'created_at']
    list_filter   = ['status']
    inlines       = [DeliveryItemInline]

@admin.register(Adjustment)
class AdjustmentAdmin(admin.ModelAdmin):
    list_display = ['reference', 'product', 'difference', 'reason', 'created_at']