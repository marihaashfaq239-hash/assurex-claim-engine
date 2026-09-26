from django.contrib import admin
from .models import Warranty, WarrantyPolicy, RuleResult


@admin.register(WarrantyPolicy)
class WarrantyPolicyAdmin(admin.ModelAdmin):
    list_display  = ['name', 'product_category', 'standard_duration_months', 'is_active']
    list_filter   = ['is_active', 'product_category']
    search_fields = ['name']


@admin.register(Warranty)
class WarrantyAdmin(admin.ModelAdmin):
    list_display  = ['product', 'warranty_type', 'start_date', 'expiry_date', 'status']
    list_filter   = ['status', 'warranty_type']
    search_fields = ['product__serial_number', 'product__product_name']
    readonly_fields = ['warranty_id']


@admin.register(RuleResult)
class RuleResultAdmin(admin.ModelAdmin):
    list_display  = ['rule_name', 'rule_type', 'outcome', 'claim', 'created_at']
    list_filter   = ['outcome', 'rule_type']
