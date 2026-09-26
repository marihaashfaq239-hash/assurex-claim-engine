from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('',                       views.product_list,       name='list'),
    path('register/',              views.product_register,   name='register'),
    path('<int:pk>/',              views.product_detail,     name='detail'),
    path('<int:pk>/edit/',         views.product_edit,       name='edit'),
    path('<int:pk>/deactivate/',   views.product_deactivate, name='deactivate'),
]
