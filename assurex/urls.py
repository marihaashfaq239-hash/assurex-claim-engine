"""
AssureX Claim Engine — Root URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from apps.accounts import views as account_views

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Landing page (public home)
    path('', account_views.landing_page, name='landing'),

    # Authentication (login, logout, register)
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),

    # Dashboard redirect based on role
    path('dashboard/', include('apps.accounts.dashboard_urls', namespace='dashboard')),

    # Customer & product/warranty management
    path('products/', include('apps.products.urls', namespace='products')),
    path('warranties/', include('apps.warranties.urls', namespace='warranties')),

    # Claims
    path('claims/', include('apps.claims.urls', namespace='claims')),

    # Reviewer
    path('reviewer/', include('apps.reviewer.urls', namespace='reviewer')),

    # Administrator
    path('administrator/', include('apps.administrator.urls', namespace='administrator')),

    # Notifications
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error pages
handler403 = 'apps.accounts.views.error_403'
handler404 = 'apps.accounts.views.error_404'
handler500 = 'apps.accounts.views.error_500'
