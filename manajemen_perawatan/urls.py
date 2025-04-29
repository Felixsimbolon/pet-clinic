from django.urls import path
from . import views

urlpatterns = [
    path('',                      views.list_treatment_types, name='treatment_list'),
    path('create/',               views.create_treatment_type, name='treatment_create'),
    path('update/<str:kode>/',    views.update_treatment_type, name='treatment_update'),
    path('delete/<str:kode>/',    views.delete_treatment_type, name='treatment_delete'),

    path('perawat',                      views.list_treatment_types_perawat, name='treatment_list_perawat'),
    path('create-perawat/',               views.create_treatment_type_perawat, name='treatment_create_perawat'),
    path('update-perawat/<str:kode>/',    views.update_treatment_type_perawat, name='treatment_update_perawat'),
    path('delete-perawat/<str:kode>/',    views.delete_treatment_type_perawat, name='treatment_delete_perawat'),
]