# example/urls.py
from django.urls import path


from canteen import views

urlpatterns = [
    path('', views.index, name='index'),
    
]