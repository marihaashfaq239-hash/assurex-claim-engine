from django.urls import path
from . import views

app_name = 'administrator'

urlpatterns = [
    path('users/',                  views.user_management,    name='users'),
    path('users/<int:pk>/toggle/',  views.toggle_user_status, name='toggle_user'),
    path('users/<int:pk>/role/',    views.change_user_role,   name='change_role'),
    path('claims/',                 views.all_claims,         name='all_claims'),
    path('warranty-policies/',      views.warranty_policies,  name='warranty_policies'),
    path('model-versions/',         views.model_versions,     name='model_versions'),
    path('thresholds/',             views.manage_thresholds,  name='thresholds'),
    path('analytics/',              views.analytics,          name='analytics'),
    path('reports/',                views.export_reports,     name='reports'),
    path('audit-logs/',             views.audit_logs,         name='audit_logs'),
    path('monitoring/',             views.monitoring,         name='monitoring'),
]
