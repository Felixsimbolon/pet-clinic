from django.urls import path
from .views import *

urlpatterns = [
    path('', daftar_perawatan, name='daftar_perawatan'),
    path('fdo', daftar_perawatan_fdo, name='daftar_perawatan_fdo'),
    path('perawat', daftar_perawatan_perawat, name='daftar_perawatan_perawat'),
    path('klien', daftar_perawatan_klien, name='daftar_perawatan_klien'),

    path('create/',create_treatment, name='create_treatment'),
    path('create-perawat/',create_treatment_perawat, name='create_treatment_perawat'),
    path('create-klien/',create_treatment_klien, name='create_treatment_klien'),
    path('create-fdo/',create_treatment_fdo, name='create_treatment_fdo'),

    path('treatments/<str:id_kunjungan>/<str:kode_perawatan>/<str:no_dokter_hewan>/<str:no_perawat_hewan>/<str:no_front_desk>/<str:nama_hewan>/<str:no_identitas_klien>/edit/', edit_treatment, name='edit_treatment'),
    path('treatments/<str:id_kunjungan>/edit-fdo/', edit_treatment_fdo, name='edit_treatment_fdo'),
    path('treatments/<str:id_kunjungan>/edit-perawat/', edit_treatment_perawat, name='edit_treatment_perawat'),
    path('treatments/<str:id_kunjungan>/edit-klien/', edit_treatment_klien, name='edit_treatment_klien'),

    path(
        'treatments/<str:id_kunjungan>/<str:kode_perawatan>/<str:no_dokter_hewan>/<str:no_perawat_hewan>/<str:no_front_desk>/<str:nama_hewan>/<str:no_identitas_klien>/delete/',
        delete_treatment,
        name='delete_treatment'
    ),


]
