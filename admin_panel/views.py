# admin_panel/views.py

from django.shortcuts import get_object_or_404, render
import requests
from django.http import HttpResponse, JsonResponse
from canteen.models import FoodDetails
from django.views.decorators.csrf import csrf_exempt
import json

def admin_panel_home(request):
    url = 'http://127.0.0.1:8000/api/food/1/fooddetails/'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return JsonResponse(data, safe=False)  # Set safe=False to allow non-dict objects to be serialized
    except requests.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)  # Return error message with status code 500

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



@csrf_exempt
def fetch_item(request, item_id):
    item = get_object_or_404(FoodDetails, id=item_id)
    data = {
        'id': item.id,
        'name': item.name,
        'stock_qty': item.stock_qty,
        'price': item.price,
        'photo_url': item.photo_url,
    }
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def update_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(FoodDetails, id=item_id)
        item.name = request.POST.get('name')
        item.stock_qty = request.POST.get('stock_qty')
        item.price = request.POST.get('price')
        item.photo_url = request.POST.get('photo_url')
        item.save()
        return HttpResponse(status=200)
    return HttpResponse(status=400)

@csrf_exempt
def remove_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(FoodDetails, id=item_id)
        item.delete()
        return HttpResponse(status=200)
    return HttpResponse(status=400)