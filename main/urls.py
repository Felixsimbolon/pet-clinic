from django.urls import path
from .views import landing_page, register_view, login_view, register_individu, register_perusahaan, register_frontdesk,register_dokter, register_perawat,dashboard_dokter, dashboard_frontdesk, dashboard_klien, dashboard_perawat

urlpatterns = [
    path('', landing_page, name='landing'),
    path('login/', login_view, name='login'),   
    path('register/', register_view, name='register'),  
    path('register/individu/', register_individu, name='register_individu'), 
    path('register/perusahaan/', register_perusahaan, name='register_perusahaan'), 
    path('register/frontdesk/', register_frontdesk, name='register_frontdesk'),
    path('register/dokter/', register_dokter, name='register_dokter'),
    path('register/perawat/', register_perawat, name='register_perawat'),
    path('dashboard/dokter/<uuid:id_dokter>/', dashboard_dokter, name='dashboard_dokter'),
    path('dashboard/perawat/<uuid:id_perawat>/', dashboard_perawat, name='dashboard_perawat'),
    path('dashboard/frontdesk/<uuid:id_frontdesk>/', dashboard_frontdesk, name='dashboard_frontdesk'),
    path('dashboard/klien/<uuid:id_klien>/', dashboard_klien, name='dashboard_klien'),
]