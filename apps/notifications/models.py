"""
AssureX — Notifications Models
Table 12: Notifications
"""
import uuid
from django.db import models
from apps.accounts.models import User


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('warranty_expiry',     'Warranty Expiry Alert'),
        ('claim_submitted',     'Claim Submitted'),
        ('claim_status',        'Claim Status Changed'),
        ('missing_docs',        'Missing Documents'),
        ('additional_info',     'Additional Info Requested'),
        ('review_complete',     'Review Completed'),
        ('claim_approved',      'Claim Approved'),
        ('claim_rejected',      'Claim Rejected'),
        ('duplicate_alert',     'Duplicate Claim Alert'),
        ('model_failure',       'Model Failure'),
        ('anomaly',             'Anomaly Detected'),
        ('system',              'System Notification'),
    ]

    PRIORITY = [
        ('low',     'Low'),
        ('medium',  'Medium'),
        ('high',    'High'),
        ('critical','Critical'),
    ]

    notification_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    recipient       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    priority        = models.CharField(max_length=10, choices=PRIORITY, default='medium')
    title           = models.CharField(max_length=200)
    message         = models.TextField()
    link            = models.CharField(max_length=500, blank=True,
        help_text='URL to navigate when clicked')

    # ── Related object ──
    object_type     = models.CharField(max_length=50, blank=True)
    object_id       = models.CharField(max_length=100, blank=True)

    # ── State ──
    is_read         = models.BooleanField(default=False)
    read_at         = models.DateTimeField(null=True, blank=True)
    is_emailed      = models.BooleanField(default=False)

    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table  = 'notifications'
        ordering  = ['-created_at']
        verbose_name = 'Notification'

    def __str__(self):
        return f'[{self.notification_type}] → {self.recipient} — {self.title}'

    def mark_read(self):
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    @classmethod
    def send(cls, recipient, notification_type, title, message, link='',
             object_type='', object_id='', priority='medium'):
        """Convenience factory method to create a notification."""
        return cls.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
            object_type=object_type,
            object_id=str(object_id),
            priority=priority,
        )
