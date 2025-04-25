from django.urls import path
from . import views

urlpatterns = [
    path('', views.daftar_kunjungan, name='daftar_kunjungan'),
    path('create-kunjungan/', views.create_kunjungan, name='create_kunjungan'),
    path('update/<str:id_kunjungan>/', views.update_kunjungan, name='update_kunjungan'),
    path('delete_kunjungan/<str:id_kunjungan>/', views.delete_kunjungan, name='delete_kunjungan'),




]
