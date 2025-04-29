from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_hewan, name='list_hewan'),
    path('create/', views.create_hewan, name='create_hewan'),
    path('update/<str:nama>/<uuid:no_identitas_klien>/', views.update_hewan, name='update_hewan'),
    path('delete/<str:nama>/<uuid:no_identitas_klien>/', views.delete_hewan, name='delete_hewan'),
]