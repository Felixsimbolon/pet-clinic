from django.urls import path
from .views import daftar_perawatan

urlpatterns = [
    path('', daftar_perawatan, name='daftar_perawatan'),
]
