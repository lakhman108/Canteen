# canteen/urls.py
from django.urls import path
from .views import index

urlpatterns = [
    path('', index, name='index'),  # Use an empty string for the base URL
    
]
