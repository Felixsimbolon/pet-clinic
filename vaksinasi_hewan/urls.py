from django.urls import path
from . import views

app_name = 'vaksinasi_hewan'
urlpatterns = [
    path('', views.index, name='index'),
    path('vaksinasi/', views.vaksinasi_hewan, name='vaksinasi_hewan'),
    path('vaksinasi-hewan/create/', views.create_vaksinasi, name='create_vaksinasi'),
    path('vaksinasi-hewan/update/<str:id_kunjungan>/', views.update_vaksinasi, name='update_vaksinasi'),
    path('vaksinasi-hewan/delete/<str:id_kunjungan>/', views.delete_vaksinasi, name='delete_vaksinasi'),
]