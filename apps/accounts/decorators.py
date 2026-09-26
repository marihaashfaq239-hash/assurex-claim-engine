"""
AssureX — Role-based access control decorators
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def role_required(*roles):
    """
    Decorator that restricts a view to users with specific roles.
    Usage:
        @role_required('reviewer', 'administrator')
        def my_view(request): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('accounts:dashboard_redirect')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


def customer_required(view_func):
    return role_required('customer')(view_func)


def employee_required(view_func):
    return role_required('employee')(view_func)


def reviewer_required(view_func):
    return role_required('reviewer')(view_func)


def admin_required(view_func):
    return role_required('administrator')(view_func)


def employee_or_admin(view_func):
    return role_required('employee', 'administrator')(view_func)


def reviewer_or_admin(view_func):
    return role_required('reviewer', 'administrator')(view_func)


def any_authenticated(view_func):
    """Just requires login — any role is fine."""
    return login_required(view_func)
