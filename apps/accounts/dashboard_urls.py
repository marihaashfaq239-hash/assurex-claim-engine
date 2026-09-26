"""
AssureX — Dashboard URL configuration
Prefix: /dashboard/
"""
from django.urls import path
from apps.accounts.views import dashboard_redirect
from apps.claims.views_customer import customer_dashboard
from apps.claims.views_employee import employee_dashboard
from apps.reviewer.views import reviewer_dashboard
from apps.administrator.views import admin_dashboard

app_name = 'dashboard'

urlpatterns = [
    path('',          dashboard_redirect,  name='index'),
    path('customer/', customer_dashboard,  name='customer'),
    path('employee/', employee_dashboard,  name='employee'),
    path('reviewer/', reviewer_dashboard,  name='reviewer'),
    path('admin/',    admin_dashboard,     name='admin'),
]
