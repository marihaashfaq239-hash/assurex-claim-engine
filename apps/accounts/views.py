"""
AssureX — Authentication Views
Handles: login, logout, register, profile, password change,
         role-based dashboard redirect, and error pages.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import User, AuditLog
from .forms import LoginForm, RegisterForm, ProfileUpdateForm, CustomPasswordChangeForm


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────

def _log_action(request, action_type, description, object_type='', object_id='', extra=None):
    """Creates an AuditLog entry."""
    ip = (request.META.get('HTTP_X_FORWARDED_FOR') or
          request.META.get('REMOTE_ADDR', ''))
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type=action_type,
        description=description,
        ip_address=ip or None,
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:300],
        object_type=object_type,
        object_id=str(object_id),
        extra_data=extra or {},
    )


def _role_dashboard_url(user):
    """Returns the correct dashboard URL for the user's role."""
    role_urls = {
        User.CUSTOMER:      '/dashboard/customer/',
        User.EMPLOYEE:      '/dashboard/employee/',
        User.REVIEWER:      '/dashboard/reviewer/',
        User.ADMINISTRATOR: '/dashboard/admin/',
    }
    return role_urls.get(user.role, '/dashboard/customer/')


# ─────────────────────────────────────────────────────────────────
# Login / Logout
# ─────────────────────────────────────────────────────────────────

@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect(_role_dashboard_url(request.user))

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            # Handle "remember me"
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)   # expires on browser close
            login(request, user)
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            _log_action(request, 'login', f'User {user.email} logged in.')
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect(_role_dashboard_url(user))
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    _log_action(request, 'logout', f'User {request.user.email} logged out.')
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('accounts:login')


# ─────────────────────────────────────────────────────────────────
# Registration
# ─────────────────────────────────────────────────────────────────

@require_http_methods(['GET', 'POST'])
def register_view(request):
    if request.user.is_authenticated:
        return redirect(_role_dashboard_url(request.user))

    form = RegisterForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            _log_action(request, 'account_created',
                        f'New account created: {user.email}',
                        object_type='User', object_id=user.pk)
            login(request, user)
            messages.success(request,
                f'Account created! Welcome to AssureX, {user.first_name}.')
            return redirect(_role_dashboard_url(user))
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'accounts/register.html', {'form': form})


# ─────────────────────────────────────────────────────────────────
# Dashboard redirect (generic /dashboard/ → role-specific URL)
# ─────────────────────────────────────────────────────────────────

@login_required
def dashboard_redirect(request):
    return redirect(_role_dashboard_url(request.user))


# ─────────────────────────────────────────────────────────────────
# Profile
# ─────────────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    form = ProfileUpdateForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user
    )
    password_form = CustomPasswordChangeForm(request.user, request.POST or None)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            if form.is_valid():
                form.save()
                _log_action(request, 'profile_updated',
                            f'{request.user.email} updated their profile.')
                messages.success(request, 'Profile updated successfully.')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Please correct the errors below.')

        elif 'change_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                _log_action(request, 'profile_updated',
                            f'{request.user.email} changed their password.')
                messages.success(request, 'Password changed successfully.')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Please correct the password errors below.')

    # Reset forms if wrong button was pressed
    if request.method == 'POST' and 'update_profile' not in request.POST:
        form = ProfileUpdateForm(instance=request.user)
    if request.method == 'POST' and 'change_password' not in request.POST:
        password_form = CustomPasswordChangeForm(request.user)

    context = {
        'form':          form,
        'password_form': password_form,
        'page_title':    'My Profile',
    }
    return render(request, 'accounts/profile.html', context)


# ─────────────────────────────────────────────────────────────────
# Error pages
# ─────────────────────────────────────────────────────────────────

def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)


# ─────────────────────────────────────────────────────────────────
# Public Landing Page
# ─────────────────────────────────────────────────────────────────

def landing_page(request):
    """Public marketing/landing page at /. Redirect authenticated users to dashboard."""
    import os
    from django.conf import settings
    from django.views.decorators.cache import never_cache
    if request.user.is_authenticated:
        return redirect(_role_dashboard_url(request.user))
    logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'images', 'logo.png')
    response = render(request, 'landing.html', {
        'logo_exists': os.path.exists(logo_path)
    })
    # Prevent browser caching of landing page
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response
