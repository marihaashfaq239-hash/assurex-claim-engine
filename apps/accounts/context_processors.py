"""
AssureX — Template Context Processors
Injects user-specific data into every template automatically.
"""


def notifications_count(request):
    """Adds unread notification count to all template contexts."""
    count = 0
    if request.user.is_authenticated:
        from apps.notifications.models import Notification
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return {'unread_notifications_count': count}


def user_role_context(request):
    """Adds role flags and sidebar template name to context."""
    if not request.user.is_authenticated:
        return {}
    role = request.user.role
    sidebar_map = {
        'customer':      'base/sidebar_customer.html',
        'employee':      'base/sidebar_employee.html',
        'reviewer':      'base/sidebar_reviewer.html',
        'administrator': 'base/sidebar_admin.html',
    }
    return {
        'user_role':          role,
        'sidebar_template':   sidebar_map.get(role, 'base/sidebar_customer.html'),
        'is_customer':        request.user.is_customer,
        'is_employee':        request.user.is_employee,
        'is_reviewer':        request.user.is_reviewer,
        'is_administrator':   request.user.is_administrator,
    }
