from django.contrib import admin
from .models import Product, ProductCategory


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'is_active', 'created_at']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['product_name', 'brand', 'category', 'serial_number', 'owner', 'purchase_date']
    list_filter   = ['category', 'brand']
    search_fields = ['product_name', 'serial_number', 'brand', 'owner__email']
    readonly_fields = ['product_id', 'created_at', 'updated_at']
