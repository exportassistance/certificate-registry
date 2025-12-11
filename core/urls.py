from django.urls import path
from . import views

urlpatterns = [
    path('cse/', views.cse_search, name='cse_search'),
    path('nika/', views.nika_search, name='nika_search'),
]