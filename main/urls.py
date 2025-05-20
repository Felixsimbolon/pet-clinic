from django.urls import path
from .views import *

urlpatterns = [
    path('', landing_page, name='landing'),
    path('login/', login_view, name='login'),   
    path('register/', register_view, name='register'),  
    path('register/individu/', register_individu, name='register_individu'), 
    path('register/perusahaan/', register_perusahaan, name='register_perusahaan'), 
    path('register/frontdesk/', register_frontdesk, name='register_frontdesk'),
    path('register/dokter/', register_dokter, name='register_dokter'),
    path('register/perawat/', register_perawat, name='register_perawat'),
    path('dashboard/dokter/', dashboard_dokter, name='dashboard_dokter'),
    path('dashboard/perawat/', dashboard_perawat, name='dashboard_perawat'),
    path('dashboard/frontdesk/', dashboard_frontdesk, name='dashboard_frontdesk'),
    path('dashboard/klien/', dashboard_klien, name='dashboard_klien'),
    path('dashboard/frontdesk/update-password/', update_password, name='update_password'),
    path('dashboard/klien/update-profile/', update_profile, name='update_profile'),
]