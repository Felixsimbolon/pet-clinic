from django.urls import path
from .views import *

urlpatterns = [
    path('', landing_page, name='landing'),
    path('logout/', logout_view, name='logout'),
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
    path('dashboard/dokter/update-password/', update_password, name='dokter_update_password'),
    path('dashboard/perawat/update-password/', update_password, name='perawat_update_password'),
    path('dashboard/frontdesk/update-password/', update_password, name='frontdesk_update_password'),
    path('dashboard/klien/update-password/', update_password, name='klien_update_password'),
    path('dashboard/dokter/update-profile/', update_profile_dokter, name='dokter_update_profile'),
    path('dashboard/perawat/update-profile/', update_profile_perawat, name='perawat_update_profile'),
    path('dashboard/frontdesk/update-profile/', update_profile_frontdesk, name='frontdesk_update_profile'),
    path('dashboard/klien/update-profile/individu/', update_profile_individu, name='klien_update_profile_individu'),
    path('dashboard/klien/update-profile/perusahaan/', update_profile_perusahaan, name='klien_update_profile_perusahaan'),
]