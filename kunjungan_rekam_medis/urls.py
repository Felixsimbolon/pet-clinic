from django.urls import path
from . import views

urlpatterns = [
    path('', views.daftar_kunjungan, name='daftar_kunjungan'),
    path('create-kunjungan/', views.create_kunjungan, name='create_kunjungan'),
    path('update/<uuid:id_kunjungan>/', views.update_kunjungan, name='update_kunjungan'),
    path('delete-kunjungan/<uuid:id_kunjungan>/', views.delete_kunjungan, name='delete_kunjungan'),
    path('create-rekam-medis/<uuid:id_kunjungan>/', views.create_rekam_medis, name='create_rekam_medis'),
    path('update-rekam-medis/<uuid:id_kunjungan>/', views.update_rekam_medis, name='update_rekam_medis'),

    





]
