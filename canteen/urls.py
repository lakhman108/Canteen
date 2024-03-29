# canteen/urls.py
from django.urls import path

from . import views
from .views import index, contact, custom_user_login, custom_user_register,custom_user_logout,show_items,cart,about,contact

app_name = 'canteen'

urlpatterns = [
    path('', index, name='index'),  # Use an empty string for the base URL
    path('contact/', contact, name='contact'),
    path('login/', custom_user_login, name='login'),
    path('register/', custom_user_register, name='register'),

    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('logout/', custom_user_logout, name='logout'),
    path('cart',cart,name='cart'),
    path('remove_order_detail/<int:order_detail_id>/', views.remove_order_detail, name='remove_order_detail'),
    path('update_order_detail/<int:order_detail_id>/<str:action>/', views.update_order_detail_quantity, name='update_order_detail_quantity'),
]
