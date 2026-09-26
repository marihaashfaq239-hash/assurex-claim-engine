"""
AssureX — Accounts Models
Table 1: Users (custom user model with roles)
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', User.ADMINISTRATOR)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    # ── Roles ──
    CUSTOMER = 'customer'
    EMPLOYEE = 'employee'
    REVIEWER = 'reviewer'
    ADMINISTRATOR = 'administrator'

    ROLE_CHOICES = [
        (CUSTOMER,      'Customer'),
        (EMPLOYEE,      'Service Center Employee'),
        (REVIEWER,      'Claim Reviewer'),
        (ADMINISTRATOR, 'Administrator'),
    ]

    # ── Fields ──
    user_id     = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    email       = models.EmailField(unique=True, db_index=True)
    first_name  = models.CharField(max_length=100)
    last_name   = models.CharField(max_length=100)
    role        = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CUSTOMER)
    phone       = models.CharField(max_length=20, blank=True)
    address     = models.TextField(blank=True)
    city        = models.CharField(max_length=100, blank=True)
    country     = models.CharField(max_length=100, default='Pakistan')
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # ── Flags ──
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    # ── Timestamps ──
    date_joined = models.DateTimeField(default=timezone.now)
    last_login  = models.DateTimeField(null=True, blank=True)
    updated_at  = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table    = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.get_full_name()} ({self.email})'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_initials(self):
        initials = ''
        if self.first_name:
            initials += self.first_name[0].upper()
        if self.last_name:
            initials += self.last_name[0].upper()
        return initials or self.email[0].upper()

    # ── Role helpers ──
    @property
    def is_customer(self):
        return self.role == self.CUSTOMER

    @property
    def is_employee(self):
        return self.role == self.EMPLOYEE

    @property
    def is_reviewer(self):
        return self.role == self.REVIEWER

    @property
    def is_administrator(self):
        return self.role == self.ADMINISTRATOR


class AuditLog(models.Model):
    """
    Table 15 (shared): Tracks every important action in the system.
    """
    ACTION_TYPES = [
        ('account_created',     'Account Created'),
        ('login',               'User Login'),
        ('logout',              'User Logout'),
        ('profile_updated',     'Profile Updated'),
        ('product_registered',  'Product Registered'),
        ('warranty_added',      'Warranty Added'),
        ('document_uploaded',   'Document Uploaded'),
        ('ocr_extracted',       'OCR Data Extracted'),
        ('data_corrected',      'Extracted Data Corrected'),
        ('claim_created',       'Claim Created'),
        ('claim_submitted',     'Claim Submitted'),
        ('claim_status_changed','Claim Status Changed'),
        ('model_predicted',     'Model Prediction Made'),
        ('reviewer_action',     'Reviewer Action'),
        ('final_decision',      'Final Decision'),
        ('ai_override',         'AI Result Overridden'),
        ('report_exported',     'Report Exported'),
        ('user_managed',        'User Managed by Admin'),
        ('policy_updated',      'Warranty Policy Updated'),
        ('threshold_updated',   'AI Threshold Updated'),
        ('anomaly_detected',    'Anomaly Detected'),
    ]

    log_id      = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    user_agent  = models.CharField(max_length=300, blank=True)
    # Optional FK to related object
    object_type = models.CharField(max_length=50, blank=True)
    object_id   = models.CharField(max_length=100, blank=True)
    extra_data  = models.JSONField(default=dict, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table  = 'audit_logs'
        ordering  = ['-created_at']
        verbose_name = 'Audit Log'

    def __str__(self):
        return f'[{self.action_type}] {self.user} — {self.created_at:%Y-%m-%d %H:%M}'
