# admin_panel/urls.py
from django.urls import path


from .views import *
from django.contrib import admin
app_name = 'admin_panel'

urlpatterns = [

    # path('', admin_panel_home, name='admin_panel_home'),
    path('filter/', filter_and_render, name='filter'),

    path('view_orders/', view_orders, name='view_orders'),
    path('mark_order_completed/', mark_order_completed, name='mark_order_completed'),

]
