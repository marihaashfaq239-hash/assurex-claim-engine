from django.contrib import admin
from .models import SystemConfiguration


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display  = ['key', 'value', 'value_type', 'updated_by', 'updated_at']
    search_fields = ['key', 'description']
    readonly_fields = ['config_id']
