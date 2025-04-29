from django.urls import path
from . import views

app_name = 'data_klien_hewan'
urlpatterns = [
    path('klien-hewan/', views.data_klien_hewan, name='data_klien_hewan'),
    path('client/<str:no_identitas>/', views.detail_client, name='detail_client'),

    # KLIEN SIDE
    path('klien-hewan-dariklien/', views.data_klien_hewan_klien, name='data_klien_hewan'),
    path('client/<str:no_identitas>/_klien', views.detail_client_klien, name='detail_client'),
]