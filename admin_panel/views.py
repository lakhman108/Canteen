from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites import requests
from django.http import request
from django.shortcuts import render, redirect

from canteen.models import *
from canteen.views import calculate_total_amount


@staff_member_required
def filter_and_render(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        if category != 'all':
            raw_data = FoodDetails.objects.filter(food__name=category).order_by('id')
        else:
         raw_data = FoodDetails.objects.all().order_by('id')
    else:
        category = 'all'
        raw_data = FoodDetails.objects.all().order_by('id')

    data = [{'id': item.id, 'name': item.name, 'stock_qty': item.stock_qty,
             'price': item.price, 'photo_url': item.photo_url} for item in raw_data]

    return render(request, 'admin_panel/admin_category.html', {'data': data, 'selected_category': category})

def get_username(user_id):
    url = f'http://localhost:8000/api/customusers/{user_id}/'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data['username']
    else:
        return "Error occurred while fetching username"


from django.shortcuts import render
import requests


def get_delivery_status(last_order_id):

    url=f'http://localhost:8000/api/orders/{last_order_id}/'
    response = requests.get(url)
    if response.status_code == 200:
        response_data = response.json()
        return response_data['delivery_status']
    else:
        return "Error occurred while fetching delivery status"


def get_remaining_orderdetails(last_order_id):
    url = f'http://localhost:8000/api/orders/{last_order_id}/orderdetails/'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        filtered_data = [item for item in data if not item['isdelivered']]
        print(filtered_data)

        return filtered_data
    pass


@staff_member_required
def view_orders(request):
    url = 'http://localhost:8000/api/orders/remainingorders/'
    response = requests.get(url)

    pending_orders_data = []
    if response.status_code == 200:
        pending_orders = response.json()
        for order in pending_orders:
            user_id = order['user']

            last_order_id = order['id']

            order_details = get_remaining_orderdetails(last_order_id)



            total_amount = calculate_total_amount(order_details)

            pending_orders_data.append({
                'order_id': last_order_id,
                'user_name': get_username(user_id),
                'user_id': user_id,
                'total_amount': total_amount,
                'order_details': order_details
            })
    else:
        # Handle the error case
        messages.error(request, "Error occurred while fetching pending orders.")
        return redirect('admin_panel:view_orders')

    context = {'orders': pending_orders_data}
    return render(request, 'admin_panel/orders.html', context)


def change_order_status(order_id):

    url = f'http://localhost:8000/api/orders/{order_id}/orderdetails/'
    response = requests.get(url)
    if response.status_code == 200:
        response_data = response.json()
        for data in response_data:
            if not  data['isdelivered']:
                return False
        return True


@staff_member_required
def mark_order_completed(request):

        order_id = request.POST.get('order_id')
        user_id = request.POST.get('user_id')
        order_detail_id = request.POST.get('order_detail_id')
        qty = request.POST.get('qty')
        print("order_id", order_id)
        print("user_id", user_id)
        print("order_detail_id", order_detail_id)
        url = f'http://localhost:8000/api/orderdetails/{order_detail_id}/'
        data = {
            "order": order_id,
            "qty": qty,
            "isdelivered": True
        }
        print(data)
        response = requests.put(url, data=data)
        print(response.status_code)

        if change_order_status(order_id):
            url = f'http://localhost:8000/api/orders/{order_id}/'
            data = {
                "delivery_status": "Delivered",
                "user": user_id
            }
            response = requests.put(url, data=data)
            print(response.status_code)

        if response.status_code == 200:
            print("Order updated successfully")
            print(response.json())
            # OrderDetails object successfully deleted
            return redirect('admin_panel:view_orders')
        else:
            # Handle the error case
            return redirect('admin_panel:view_orders')

        return redirect('admin_panel:view_orders:view_orders')