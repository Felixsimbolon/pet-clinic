from django.urls import path
from . import views

urlpatterns = [
    path('',                            views.list_medicines,          name='medicine_list'),
    path('create/',                     views.create_medicine,         name='medicine_create'),
    path('update/<str:kode>/',          views.update_medicine,         name='medicine_update'),
    path('update-stock/<str:kode>/',    views.update_medicine_stock,   name='medicine_update_stock'),
    path('delete/<str:kode>/',          views.delete_medicine,         name='medicine_delete'),

    path('perawat',                            views.list_medicines_perawat,          name='medicine_list_perawat'),
    path('create-perawat/',                     views.create_medicine_perawat,         name='medicine_create_perawat'),
    path('update-perawat/<str:kode>/',          views.update_medicine_perawat,         name='medicine_update_perawat'),
    path('update-stock-perawat/<str:kode>/',    views.update_medicine_stock_perawat,   name='medicine_update_stock_perawat'),
    path('delete-perawat/<str:kode>/',          views.delete_medicine_perawat,         name='medicine_delete_perawat'),
]
