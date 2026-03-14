from django.contrib import admin
from .models import Product, Category, Warehouse, Location

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['name', 'sku', 'category', 'current_stock', 'is_active']
    search_fields = ['name', 'sku']
    list_filter   = ['category', 'warehouse', 'is_active']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_code', 'address']

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_code', 'warehouse']