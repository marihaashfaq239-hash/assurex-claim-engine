"""
AssureX — Products Models
Table 2: Products
"""
import uuid
from django.db import models
from django.utils import timezone
from apps.accounts.models import User


class ProductCategory(models.Model):
    """Configurable product categories (managed by Admin)."""
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=50, default='bi-box-seam')
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table  = 'product_categories'
        ordering  = ['name']
        verbose_name_plural = 'Product Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Table 2: Registered Products.
    Each product is owned by a user and has a unique Product ID.
    """
    product_id      = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    owner           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    registered_by   = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products_registered',
        help_text='Set if a service center employee registered on behalf of customer'
    )

    # ── Product Details ──
    product_name    = models.CharField(max_length=200)
    brand           = models.CharField(max_length=100)
    category        = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, related_name='products')
    model_number    = models.CharField(max_length=100)
    serial_number   = models.CharField(max_length=200, db_index=True)

    # ── Purchase Details ──
    purchase_date   = models.DateField()
    purchase_price  = models.DecimalField(max_digits=12, decimal_places=2)
    retailer        = models.CharField(max_length=200)
    purchase_city   = models.CharField(max_length=100, blank=True)

    # ── Warranty Duration ──
    warranty_duration_months = models.PositiveIntegerField(default=12)

    # ── Metadata ──
    notes           = models.TextField(blank=True)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table  = 'products'
        ordering  = ['-created_at']
        verbose_name = 'Product'

    def __str__(self):
        return f'{self.brand} {self.product_name} — SN: {self.serial_number}'

    @property
    def product_age_months(self):
        """Returns product age in months from purchase date."""
        from dateutil.relativedelta import relativedelta
        today = timezone.now().date()
        delta = relativedelta(today, self.purchase_date)
        return delta.years * 12 + delta.months

    @property
    def product_age_years(self):
        from dateutil.relativedelta import relativedelta
        today = timezone.now().date()
        delta = relativedelta(today, self.purchase_date)
        return round(delta.years + delta.months / 12, 1)
