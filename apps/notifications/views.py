"""
AssureX — Notifications Views
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')

    # Mark all as read when user views the list
    unread = notifications.filter(is_read=False)
    for n in unread:
        n.mark_read()

    context = {
        'notifications': notifications,
        'page_title':    'Notifications',
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
@require_POST
def mark_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, recipient=request.user)
    n.mark_read()
    return JsonResponse({'status': 'ok'})
