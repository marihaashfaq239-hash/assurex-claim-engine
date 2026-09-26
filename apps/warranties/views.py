"""
AssureX — Warranties Views
SRS §1.6.iv, §1.6.viii, §1.6.ix
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from .models import Warranty
from .forms import WarrantyAddForm
from apps.products.models import Product
from apps.notifications.models import Notification


def _send_expiry_alert_if_needed(warranty, user):
    """
    Send a single warranty_expiry notification if one hasn't been sent today.
    Called on warranty list/detail view so users get real-time alerts.
    SRS §1.6.ix: Administrators can configure the number of days before expiry.
    """
    try:
        from apps.administrator.models import SystemConfiguration
        alert_days = SystemConfiguration.get('warranty_expiry_alert_days', 30)
        # SystemConfiguration may return a list; take the max window for real-time check
        if isinstance(alert_days, list):
            alert_days = max(alert_days)
    except Exception:
        alert_days = 30

    today = timezone.now().date()

    if not warranty.expiry_date:
        return
    days_remaining = (warranty.expiry_date - today).days

    # Only alert if within the configured window and not expired
    if not (0 <= days_remaining <= alert_days):
        return

    # Don't send duplicate alert for the same warranty today
    already_sent = Notification.objects.filter(
        recipient=user,
        notification_type='warranty_expiry',
        object_type='Warranty',
        object_id=str(warranty.pk),
        created_at__date=today,
    ).exists()

    if already_sent:
        return

    # Determine urgency & priority
    if days_remaining == 0:
        urgency, priority = 'expires TODAY', 'critical'
    elif days_remaining == 1:
        urgency, priority = 'expires TOMORROW', 'critical'
    elif days_remaining <= 7:
        urgency, priority = f'expires in {days_remaining} days', 'high'
    elif days_remaining <= 14:
        urgency, priority = f'expires in {days_remaining} days', 'medium'
    else:
        urgency, priority = f'expires in {days_remaining} days', 'low'

    product = warranty.product
    Notification.send(
        recipient=user,
        notification_type='warranty_expiry',
        title=f'Warranty Expiry Alert — {product.product_name}',
        message=(
            f'Your warranty for {product.brand} {product.product_name} '
            f'(Serial: {product.serial_number}) {urgency} on {warranty.expiry_date}. '
            f'Submit any claims before the warranty expires.'
        ),
        link=f'/warranties/{warranty.pk}/',
        object_type='Warranty',
        object_id=warranty.pk,
        priority=priority,
    )


@login_required
def warranty_list(request):
    """
    All warranties for the logged-in customer's products.
    SRS §1.6.viii: displays remaining period, active/expired/expiring status.
    SRS §1.6.ix: fires real-time expiry alerts while user is browsing.
    """
    warranties = Warranty.objects.filter(
        product__owner=request.user
    ).select_related('product', 'product__category').order_by('expiry_date')

    today = timezone.now().date()
    for w in warranties:
        w.update_status()
        # Fire alert if expiry is approaching (SRS §1.6.ix)
        _send_expiry_alert_if_needed(w, request.user)

    active    = [w for w in warranties if w.status in ('active', 'expiring')]
    expired   = [w for w in warranties if w.status == 'expired']
    expiring  = [w for w in warranties if w.status == 'expiring']

    context = {
        'active_warranties':  active,
        'expired_warranties': expired,
        'expiring_warranties':expiring,
        'today':              today,
        'page_title':         'My Warranties',
    }
    return render(request, 'warranties/warranty_list.html', context)


@login_required
def warranty_detail(request, pk):
    """
    Warranty detail view — also triggers expiry alert check.
    SRS §1.6.viii, §1.6.ix
    """
    warranty = get_object_or_404(
        Warranty, pk=pk, product__owner=request.user
    )
    warranty.update_status()
    _send_expiry_alert_if_needed(warranty, request.user)

    context = {
        'warranty':   warranty,
        'page_title': f'Warranty — {warranty.product.product_name}',
    }
    return render(request, 'warranties/warranty_detail.html', context)


@login_required
def warranty_add(request):
    """
    Manually add an extended / third-party warranty for an existing product.
    SRS §1.6.viii: Customer can attach additional warranty documents.
    """
    form = WarrantyAddForm(
        request.POST or None,
        request.FILES or None,
        user=request.user,
    )

    if request.method == 'POST' and form.is_valid():
        warranty = form.save(commit=False)
        # Verify the product belongs to the logged-in user
        if warranty.product.owner != request.user:
            messages.error(request, 'You cannot add a warranty to a product you do not own.')
            return redirect('warranties:list')
        warranty.status = 'active'
        warranty.save()

        Notification.send(
            recipient=request.user,
            notification_type='system',
            title='Warranty Added',
            message=(
                f'A new {warranty.get_warranty_type_display()} warranty from '
                f'{warranty.warranty_provider} has been added to '
                f'{warranty.product.brand} {warranty.product.product_name}. '
                f'It expires on {warranty.expiry_date}.'
            ),
            link=f'/warranties/{warranty.pk}/',
            object_type='Warranty',
            object_id=warranty.pk,
        )

        messages.success(
            request,
            f'Warranty from {warranty.warranty_provider} added successfully '
            f'for {warranty.product.product_name}.'
        )
        return redirect('warranties:detail', pk=warranty.pk)

    context = {
        'form':       form,
        'page_title': 'Add Warranty',
    }
    return render(request, 'warranties/warranty_add.html', context)
