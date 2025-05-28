from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_hewan, name='list_hewan'),
    path('create/', views.create_hewan, name='create_hewan'),
    path('hewan/<str:nama>/<uuid:no_identitas_klien>/delete/', views.delete_hewan, name='delete_hewan'),
    path('hewan/<str:nama>/<uuid:no_identitas_klien>/update/', views.update_hewan, name='update_hewan'),
]