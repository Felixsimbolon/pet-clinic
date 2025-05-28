from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_jenis_hewan, name='list_jenis_hewan'),
    path('create/', views.create_jenis_hewan, name='create_jenis_hewan'),
    path('update/<uuid:id_jenis>/', views.update_jenis_hewan, name='update_jenis_hewan'),
    path('delete/<uuid:id_jenis>/', views.delete_jenis_hewan, name='delete_jenis_hewan'),
]