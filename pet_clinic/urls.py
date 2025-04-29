"""
URL configuration for pet_clinic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('perawatan/',include('kunjungan_perawatan.urls')),
    path('kunjungan_rekam_medis/', include('kunjungan_rekam_medis.urls')),
    path('manajemen_obat/', include('manajemen_obat.urls')),
    path('manajemen_perawatan/', include('manajemen_perawatan.urls')),
    path('pemberian_obat/', include('pemberian_obat.urls')),
    path('rekam/',include('kunjungan_rekam_medis.urls')),
    path('data_klien_hewan/', include('data_klien_hewan.urls')),
    path('manajemen_vaksinasi/', include('manajemen_vaksinasi.urls')),
]
