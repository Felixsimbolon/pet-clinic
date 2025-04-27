from django.urls import path
from . import views

app_name = 'merah'

urlpatterns = [
    path('', views.index, name='index'),
    path('vaksinasi/', views.vaksinasi_hewan, name='vaksinasi_hewan'),
    path('stok-vaksin/', views.data_stok_vaksin, name='data_stok_vaksin'),
    path('klien-hewan/', views.data_klien_hewan, name='data_klien_hewan'),
    path('vaksinasi-hewan/create/', views.create_vaksinasi, name='create_vaksinasi'),
    path('vaksinasi-hewan/update/<str:id_kunjungan>/', views.update_vaksinasi, name='update_vaksinasi'),
    path('vaksinasi-hewan/delete/<str:id_kunjungan>/', views.delete_vaksinasi, name='delete_vaksinasi'),

    path('client/<str:no_identitas>/', views.detail_client, name='detail_client'),
    path('create-vaccine/', views.create_vaccine, name='create_vaccine'),
    path('add-vaccine-stock/', views.add_vaccine_stock, name='add_vaccine_stock'),
    path('edit-vaccine/<uuid:id_vaksin>/', views.edit_vaccine, name='edit_vaccine'),
    path('delete-vaccine/<uuid:id_vaksin>/', views.delete_vaccine, name='delete_vaccine'),

    path('stok-vaksin/', views.data_stok_vaksin, name='stok_vaksin'),
    path('stok-vaksin/create/', views.create_vaccine, name='create_vaccine'),
    path('stok-vaksin/edit/<str:kode_vaksin>/', views.edit_vaccine, name='edit_vaccine'),
    path('stok-vaksin/update-stock/', views.add_vaccine_stock, name='add_vaccine_stock'),
    path('stok-vaksin/delete/<str:kode_vaksin>/', views.delete_vaccine, name='delete_vaccine'),
]