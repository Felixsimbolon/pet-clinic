# manajemen_obat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',                            views.list_medicines,          name='medicine_list'),
    path('create/',                     views.create_medicine,         name='medicine_create'),
    path('update/<str:kode>/',          views.update_medicine,         name='medicine_update'),
    path('update-stock/<str:kode>/',    views.update_medicine_stock,   name='medicine_update_stock'),
    path('delete/<str:kode>/',          views.delete_medicine,         name='medicine_delete'),
]
