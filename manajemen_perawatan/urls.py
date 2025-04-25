from django.urls import path
from . import views

urlpatterns = [
    path('',                      views.list_treatment_types, name='treatment_list'),
    path('create/',               views.create_treatment_type, name='treatment_create'),
    path('update/<str:kode>/',    views.update_treatment_type, name='treatment_update'),
    path('delete/<str:kode>/',    views.delete_treatment_type, name='treatment_delete'),
]