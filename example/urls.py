# example/urls.py
from django.urls import path

from example.views import index
from example import views

urlpatterns = [
    path('', index),
   path('contact/',views.contanct,name="contanct"),
]