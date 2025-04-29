from django.urls import path
from . import views

app_name = 'data_stok_vaksin'
urlpatterns = [
    path('', views.index, name='index'),
    path('stok-vaksin/', views.data_stok_vaksin, name='data_stok_vaksin'),
    path('create-vaccine/', views.create_vaccine, name='create_vaccine'),
    path('add-vaccine-stock/', views.add_vaccine_stock, name='add_vaccine_stock'),
    path('edit-vaccine/<str:kode>/', views.edit_vaccine, name='edit_vaccine'),
    path('delete-vaccine/<str:kode>/', views.delete_vaccine, name='delete_vaccine'),
]