from django.urls import path
from .views import index, contact, custom_user_login, custom_user_register

app_name = 'example'  # Add this line to set the app_name


urlpatterns = [
    path('', index, name='index'),
    path('contact/', contact, name='contact'),
    path('login/', custom_user_login, name='login'),
    path('register/', custom_user_register, name='register'),
]
