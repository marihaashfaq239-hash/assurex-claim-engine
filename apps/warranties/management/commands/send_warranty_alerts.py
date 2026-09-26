"""
AssureX — Management Command: send_warranty_alerts
SRS §1.6.ix — Warranty Expiry Alerts

Sends in-app notifications (and optionally email) to users whose product
warranties are expiring within the configured alert window.

Usage:
    python manage.py send_warranty_alerts
    python manage.py send_warranty_alerts --days 14
    python manage.py send_warranty_alerts --dry-run

Schedule with cron (daily at 8 AM):
    0 8 * * * cd /path/to/project && python manage.py send_warranty_alerts
"""
from __future__ import annotations
import logging
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from apps.warranties.models import Warranty
from apps.notifications.models import Notification
from apps.accounts.models import AuditLog

logger = logging.getLogger(__name__)


# ── Configurable alert thresholds (days before expiry) ──
# Admins can override WARRANTY_EXPIRY_ALERT_DAYS in settings or SystemConfiguration
DEFAULT_ALERT_WINDOWS = [30, 14, 7, 1]   # send alerts at these day-thresholds


def _get_alert_days() -> list[int]:
    """
    Load alert day windows from SystemConfiguration (runtime-configurable).
    Falls back to DEFAULT_ALERT_WINDOWS if not configured.
    """
    try:
        from apps.administrator.models import SystemConfiguration
        import json
        raw = SystemConfiguration.get('warranty_expiry_alert_days', None)
        if raw is not None:
            if isinstance(raw, list):
                return [int(d) for d in raw]
            return [int(raw)]
    except Exception:
        pass
    # Also check Django settings
    days = getattr(settings, 'WARRANTY_EXPIRY_ALERT_DAYS', None)
    if days:
        return [days] if isinstance(days, int) else list(days)
    return DEFAULT_ALERT_WINDOWS


class Command(BaseCommand):
    help = (
        'Send warranty expiry notifications to customers whose warranties '
        'are approaching expiry. Run this daily via cron.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--days', type=int, default=None,
            help='Override alert window (days before expiry). Default: use configured windows.'
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Preview what notifications would be sent without actually sending.'
        )

    def handle(self, *args, **options):
        dry_run     = options['dry_run']
        days_override = options['days']
        today       = timezone.now().date()

        alert_windows = [days_override] if days_override else _get_alert_days()

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f'AssureX — Warranty Expiry Alerts'
                f' | Date: {today} | Windows: {alert_windows} days'
                f'{" | DRY RUN" if dry_run else ""}'
            )
        )

        total_sent = 0
        total_skipped = 0

        for days in alert_windows:
            target_date = today + timedelta(days=days)
            # Find warranties expiring exactly on target_date (active/expiring only)
            warranties = Warranty.objects.filter(
                expiry_date=target_date,
                status__in=['active', 'expiring'],
            ).select_related('product', 'product__owner')

            if not warranties.exists():
                self.stdout.write(f'  {days:>3} days: no warranties expiring on {target_date}')
                continue

            for warranty in warranties:
                user    = warranty.product.owner
                product = warranty.product

                # Skip if a warranty_expiry notification was already sent today for this warranty
                already_sent = Notification.objects.filter(
                    recipient=user,
                    notification_type='warranty_expiry',
                    object_type='Warranty',
                    object_id=str(warranty.pk),
                    created_at__date=today,
                ).exists()

                if already_sent:
                    total_skipped += 1
                    self.stdout.write(
                        f'  {days:>3} days: SKIP (already sent today) '
                        f'— {user.email} | {product.brand} {product.product_name}'
                    )
                    continue

                # Determine priority based on urgency
                if days <= 1:
                    priority = 'critical'
                    urgency  = 'EXPIRES TOMORROW'
                elif days <= 7:
                    priority = 'high'
                    urgency  = f'expires in {days} days'
                elif days <= 14:
                    priority = 'medium'
                    urgency  = f'expires in {days} days'
                else:
                    priority = 'low'
                    urgency  = f'expires in {days} days'

                title = f'Warranty Expiry Alert — {product.product_name}'
                message = (
                    f'Your warranty for {product.brand} {product.product_name} '
                    f'(Serial: {product.serial_number}) {urgency} on {warranty.expiry_date}. '
                    f'If you have a claim to submit, please do so before the warranty expires. '
                    f'Warranty Provider: {warranty.warranty_provider}.'
                )

                if not dry_run:
                    Notification.send(
                        recipient=user,
                        notification_type='warranty_expiry',
                        title=title,
                        message=message,
                        link=f'/warranties/{warranty.pk}/',
                        object_type='Warranty',
                        object_id=warranty.pk,
                        priority=priority,
                    )
                    # Update warranty status to 'expiring'
                    if warranty.status != 'expiring':
                        warranty.status = 'expiring'
                        warranty.save(update_fields=['status'])

                total_sent += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  {days:>3} days: {"[DRY] " if dry_run else "SENT  "}'
                        f'[{priority.upper()}] {user.email} — '
                        f'{product.brand} {product.product_name} — expires {warranty.expiry_date}'
                    )
                )

        # Log the run to AuditLog (not on dry-run)
        if not dry_run and total_sent > 0:
            try:
                AuditLog.objects.create(
                    user=None,
                    action_type='anomaly_detected',   # closest available type
                    description=(
                        f'Warranty expiry alerts sent: {total_sent} notifications '
                        f'dispatched, {total_skipped} skipped (already sent today).'
                    ),
                )
            except Exception:
                pass

        summary = (
            f'\nDone. '
            f'{"Would send" if dry_run else "Sent"}: {total_sent} notifications | '
            f'Skipped (duplicate today): {total_skipped}'
        )
        self.stdout.write(self.style.SUCCESS(summary))
