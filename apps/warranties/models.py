"""
AssureX — Warranties Models
Tables: 3 (Warranties), 9 (Warranty_Rules), 10 (Rule_Results)
"""
import uuid
from django.db import models
from django.utils import timezone
from apps.accounts.models import User
from apps.products.models import Product


class WarrantyPolicy(models.Model):
    """
    Table 9: Warranty Rules / Policies (configurable, not hard-coded).
    Can be loaded from JSON/YAML policy files or managed via Admin UI.
    """
    policy_id       = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name            = models.CharField(max_length=200)
    product_category = models.ForeignKey(
        'products.ProductCategory', on_delete=models.CASCADE, related_name='warranty_policies'
    )
    # Coverage
    standard_duration_months  = models.PositiveIntegerField(default=12)
    extended_duration_months  = models.PositiveIntegerField(default=0)
    claim_reporting_period_days = models.PositiveIntegerField(default=14,
        help_text='Max days after fault to report claim')
    # Covered faults (JSON list)
    covered_faults  = models.JSONField(default=list,
        help_text='List of covered fault types')
    # Exclusions (JSON list)
    exclusions      = models.JSONField(default=list,
        help_text='List of excluded fault types / conditions')
    # Documents required (JSON list)
    mandatory_documents = models.JSONField(default=list,
        help_text='List of required document types')
    # Repair conditions
    authorized_repair_required = models.BooleanField(default=True)
    max_repair_count    = models.PositiveIntegerField(default=2,
        help_text='Max prior repairs before claim invalid')
    # Replacement conditions
    replacement_allowed = models.BooleanField(default=False)
    grace_period_days   = models.PositiveIntegerField(default=7)
    # Rules stored as JSON (hard-fail, warning, manual-review)
    hard_fail_rules     = models.JSONField(default=list)
    warning_rules       = models.JSONField(default=list)
    manual_review_rules = models.JSONField(default=list)
    # Source file
    policy_file     = models.CharField(max_length=255, blank=True,
        help_text='Source JSON/YAML policy filename')
    is_active       = models.BooleanField(default=True)
    created_by      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table  = 'warranty_policies'
        verbose_name = 'Warranty Policy'
        verbose_name_plural = 'Warranty Policies'

    def __str__(self):
        return f'{self.name} ({self.product_category})'


class Warranty(models.Model):
    """
    Table 3: Warranty Records tied to a specific product instance.
    """
    WARRANTY_STATUS = [
        ('active',    'Active'),
        ('expired',   'Expired'),
        ('expiring',  'Expiring Soon'),
        ('extended',  'Extended'),
        ('void',      'Void'),
    ]

    WARRANTY_TYPE = [
        ('standard',  'Standard'),
        ('extended',  'Extended'),
        ('third_party', 'Third Party'),
    ]

    warranty_id     = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    product         = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='warranties')
    policy          = models.ForeignKey(WarrantyPolicy, on_delete=models.PROTECT,
                                        null=True, blank=True, related_name='warranties')
    warranty_type   = models.CharField(max_length=20, choices=WARRANTY_TYPE, default='standard')

    # ── Provider & Dates ──
    warranty_provider   = models.CharField(max_length=200, default='Manufacturer')
    service_center      = models.CharField(max_length=200, blank=True)
    start_date          = models.DateField()
    expiry_date         = models.DateField()

    # ── Coverage ──
    coverage_description = models.TextField(blank=True)
    exclusions           = models.TextField(blank=True)

    # ── Status ──
    status          = models.CharField(max_length=20, choices=WARRANTY_STATUS, default='active')
    is_active       = models.BooleanField(default=True)

    # ── Documents ──
    warranty_card   = models.FileField(upload_to='warranty_cards/', blank=True, null=True)

    # ── Timestamps ──
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table  = 'warranties'
        ordering  = ['-start_date']
        verbose_name = 'Warranty'
        verbose_name_plural = 'Warranties'

    def __str__(self):
        return f'Warranty [{self.warranty_id}] — {self.product} ({self.status})'

    @property
    def remaining_days(self):
        today = timezone.now().date()
        if self.expiry_date >= today:
            return (self.expiry_date - today).days
        return 0

    @property
    def is_expired(self):
        return timezone.now().date() > self.expiry_date

    @property
    def is_expiring_soon(self):
        from django.conf import settings
        days = getattr(settings, 'WARRANTY_EXPIRY_ALERT_DAYS', 30)
        today = timezone.now().date()
        return 0 < (self.expiry_date - today).days <= days

    def update_status(self):
        if self.is_expired:
            self.status = 'expired'
        elif self.is_expiring_soon:
            self.status = 'expiring'
        else:
            self.status = 'active'
        self.save(update_fields=['status'])


class RuleResult(models.Model):
    """
    Table 10: Rule check results for a specific claim evaluation.
    """
    RULE_OUTCOME = [
        ('pass',    'Pass'),
        ('fail',    'Fail'),
        ('warning', 'Warning'),
        ('skip',    'Skipped'),
    ]

    claim       = models.ForeignKey('claims.Claim', on_delete=models.CASCADE, related_name='rule_results')
    rule_name   = models.CharField(max_length=200)
    rule_type   = models.CharField(max_length=20,
        choices=[('hard_fail','Hard Fail'),('warning','Warning'),('manual_review','Manual Review')])
    outcome     = models.CharField(max_length=10, choices=RULE_OUTCOME)
    description = models.TextField(blank=True)
    detail      = models.JSONField(default=dict, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table  = 'rule_results'
        ordering  = ['rule_name']

    def __str__(self):
        return f'{self.rule_name}: {self.outcome}'
