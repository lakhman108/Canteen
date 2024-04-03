from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites import requests
from django.shortcuts import render, redirect

from canteen.models import *


def filter_and_render(request):
   if request.method == 'POST':
        category = request.POST.get('category')
        raw_data = FoodDetails.objects.filter(food__name=category).order_by('id')
   else:
        category = 'all'
        raw_data = FoodDetails.objects.all().order_by('id')

   data = [{'id': item.id, 'name': item.name, 'stock_qty': item.stock_qty,
             'price': item.price, 'photo_url': item.photo_url} for item in raw_data]
    
   return render(request, 'admin_panel/admin_category.html', {'data': data, 'selected_category': category})
