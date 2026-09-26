"""
AssureX — Administrator app models.
Stores system-wide configuration that admins can change at runtime.
"""
import uuid
from django.db import models
from apps.accounts.models import User


class SystemConfiguration(models.Model):
    """
    Key-value store for runtime-configurable system settings.
    Admins can tune AI thresholds, expiry alert days, etc. without code changes.
    """
    config_id   = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    key         = models.CharField(max_length=100, unique=True, db_index=True)
    value       = models.TextField()
    value_type  = models.CharField(max_length=20,
        choices=[('str','String'),('int','Integer'),('float','Float'),('bool','Boolean'),('json','JSON')],
        default='str')
    description = models.TextField(blank=True)
    updated_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table     = 'system_configuration'
        verbose_name = 'System Configuration'

    def __str__(self):
        return f'{self.key} = {self.value}'

    def get_typed_value(self):
        import json
        converters = {
            'int':   int,
            'float': float,
            'bool':  lambda v: v.lower() in ('true', '1', 'yes'),
            'json':  json.loads,
            'str':   str,
        }
        return converters.get(self.value_type, str)(self.value)

    @classmethod
    def get(cls, key, default=None):
        try:
            obj = cls.objects.get(key=key)
            return obj.get_typed_value()
        except cls.DoesNotExist:
            return default
