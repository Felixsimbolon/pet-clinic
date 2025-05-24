from django.urls import path
from . import views

urlpatterns = [
    path('', views.daftar_kunjungan, name='daftar_kunjungan'),
    path('fdo', views.daftar_kunjungan_fdo, name='daftar_kunjungan_fdo'),
    path('klien', views.daftar_kunjungan_klien, name='daftar_kunjungan_klien'),
    path('perawat', views.daftar_kunjungan_perawat, name='daftar_kunjungan_perawat'),
    
    path('create-kunjungan/', views.create_kunjungan, name='create_kunjungan'),
    path('update/<str:id_kunjungan>/<str:no_dokter_hewan>/<str:no_perawat_hewan>/<str:no_front_desk>/<str:nama_hewan>/<str:no_identitas_klien>/', views.update_kunjungan, name='update_kunjungan'),
    path('delete-kunjungan/<str:id_kunjungan>/<str:no_dokter_hewan>/<str:no_perawat_hewan>/<str:no_front_desk>/<str:nama_hewan>/<str:no_identitas_klien>/', 
        views.delete_kunjungan, name='delete_kunjungan'),
    path('create-rekam-medis/<str:id_kunjungan>/<str:no_dokter_hewan>/<str:no_perawat_hewan>/<str:no_front_desk>/<str:nama_hewan>/<str:no_identitas_klien>/', views.create_rekam_medis, name='create_rekam_medis'),
    path('update-rekam-medis/<str:id_kunjungan>/<str:no_dokter_hewan>/<str:no_perawat_hewan>/<str:no_front_desk>/<str:nama_hewan>/<str:no_identitas_klien>/', views.update_rekam_medis, name='update_rekam_medis'),
    
    path('rekam-medis/<str:id_kunjungan>/<str:no_dokter_hewan>/<str:no_perawat_hewan>/<str:no_front_desk>/<str:nama_hewan>/<str:no_identitas_klien>/', views.rekam_medis_view, name='rekam_medis_view'),
    path('rekam-medis/<str:id_kunjungan>/<str:no_dokter_hewan>/<str:no_perawat_hewan>/<str:no_front_desk>/<str:nama_hewan>/<str:no_identitas_klien>/perawat', views.rekam_medis_view_perawat, name='rekam_medis_view_perawat'),
    path('rekam-medis/<str:id_kunjungan>/<str:no_dokter_hewan>/<str:no_perawat_hewan>/<str:no_front_desk>/<str:nama_hewan>/<str:no_identitas_klien>/klien', views.rekam_medis_view_klien, name='rekam_medis_view_klien'),
    path('rekam-medis/<str:id_kunjungan>/<str:no_dokter_hewan>/<str:no_perawat_hewan>/<str:no_front_desk>/<str:nama_hewan>/<str:no_identitas_klien>/fdo', views.rekam_medis_view_fdo, name='rekam_medis_view_fdo'),

    

    

#id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien
    





]
