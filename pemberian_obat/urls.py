from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_prescriptions, name='prescription_list'),
    path('create/', views.create_prescription, name='prescription_create'),
    path('delete/', views.delete_prescription, name='prescription_delete'),

    path('client/', views.list_prescriptions_client, name='prescription_list_client'),
]