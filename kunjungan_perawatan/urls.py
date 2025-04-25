from django.urls import path
from .views import daftar_perawatan,create_treatment,edit_treatment,delete_treatment

urlpatterns = [
    path('', daftar_perawatan, name='daftar_perawatan'),
    path('create/',create_treatment, name='create_treatment'),
    path('treatments/<str:id_kunjungan>/edit/', edit_treatment, name='edit_treatment'),
    path(
        'treatments/<str:id_kunjungan>/<str:kode_perawatan>/delete/',
        delete_treatment,
        name='delete_treatment'
    ),


]
