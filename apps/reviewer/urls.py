from django.urls import path
from . import views

app_name = 'reviewer'

urlpatterns = [
    path('queue/',             views.review_queue,     name='queue'),
    path('reviewed/',          views.reviewed_claims,  name='reviewed'),
    path('overrides/',         views.override_history, name='overrides'),
    path('<int:pk>/review/',   views.review_detail,    name='detail'),
]
