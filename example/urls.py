# example/urls.py
from django.urls import path

from example.views import index
from example import views

urlpatterns = [
    path('', views.index, name='index'),
    path('contanct/', views.contanct, name="contanct"),
]