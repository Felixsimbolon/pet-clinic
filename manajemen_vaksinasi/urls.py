from django.urls import path, include
from . import views

app_name = 'manajemen_vaksinasi'

urlpatterns = [
    # Halaman utama
    path('', views.index, name='index'),
    path('klien/', views.index2, name='index2'),
    
    # Data stok vaksin
    path('stok-vaksin/', views.data_stok_vaksin, name='data_stok_vaksin'),
    path('stok-vaksin/create/', views.create_vaccine, name='create_vaccine'),
    path('stok-vaksin/add-stock/', views.add_vaccine_stock, name='add_vaccine_stock'),
    path('stok-vaksin/edit/<str:kode>/', views.edit_vaccine, name='edit_vaccine'),
    path('stok-vaksin/delete/<str:kode>/', views.delete_vaccine, name='delete_vaccine'),
    
    # Vaksinasi hewan
    path('vaksinasi/', views.vaksinasi_hewan, name='vaksinasi_hewan'),
    path('vaksinasi/create/', views.create_vaksinasi, name='create_vaksinasi'),
    path('vaksinasi/update/<str:id_kunjungan>/', views.update_vaksinasi, name='update_vaksinasi'),
    path('vaksinasi/delete/<str:id_kunjungan>/', views.delete_vaksinasi, name='delete_vaksinasi'),
    path('vaksinasi-klien/', views.vaksinasi_hewan_klien, name='vaksinasi_hewan_klien'),
]