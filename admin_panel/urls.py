# admin_panel/urls.py
from django.urls import path
from .views import *

app_name = 'admin_panel'

urlpatterns = [
    # path('', admin_panel_home, name='admin_panel_home'),
    path('filter/', filter_and_render, name='filter'),
    # path('fetch_item/<int:item_id>/', fetch_item, name='fetch_item'),
    # path('update_item/<int:item_id>/', update_item, name='update_item'),
    # path('remove_item/<int:item_id>/', remove_item, name='remove_item'),
    # path('view_orders/', view_orders, name='view_orders'),
    # path('mark_order_completed/', mark_order_completed, name='mark_order_completed'),

]
