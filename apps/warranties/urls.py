from django.urls import path
from . import views

app_name = 'warranties'

urlpatterns = [
    path('',          views.warranty_list,   name='list'),
    path('add/',      views.warranty_add,    name='add'),
    path('<int:pk>/', views.warranty_detail, name='detail'),
]
