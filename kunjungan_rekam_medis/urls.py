from django.urls import path
from . import views

urlpatterns = [
    path('', views.daftar_kunjungan, name='daftar_kunjungan'),
    path('fdo', views.daftar_kunjungan_fdo, name='daftar_kunjungan_fdo'),
    path('klien', views.daftar_kunjungan_klien, name='daftar_kunjungan_klien'),
    path('perawat', views.daftar_kunjungan_perawat, name='daftar_kunjungan_perawat'),
    
    path('rekam-medis-dummy',views.create_rekam_medis_dummy, name='create_rekam_medis_dummy'),
    path('rekam-medis-dummy-fdo',views.create_rekam_medis_dummy_fdo, name='create_rekam_medis_dummy_fdo'),
    path('rekam-medis-dummy-perawat',views.create_rekam_medis_dummy_perawat, name='create_rekam_medis_dummy_perawat'),
    path('rekam-medis-dummy-klien',views.create_rekam_medis_dummy_klien, name='create_rekam_medis_dummy_klien'),



    path('create-kunjungan/', views.create_kunjungan, name='create_kunjungan'),
    path('update/<uuid:id_kunjungan>/', views.update_kunjungan, name='update_kunjungan'),
    path('delete-kunjungan/<uuid:id_kunjungan>/', views.delete_kunjungan, name='delete_kunjungan'),
    path('create-rekam-medis/<uuid:id_kunjungan>/', views.create_rekam_medis, name='create_rekam_medis'),
    path('update-rekam-medis/<uuid:id_kunjungan>/', views.update_rekam_medis, name='update_rekam_medis'),
    path('rekam-medis/<uuid:id_kunjungan>/', views.rekam_medis_view, name='rekam_medis'),
    path('rekam-medis-dummy-update',views.update_rekam_medis_dummy, name='update_rekam_medis_dummy')
    

    


    





]
