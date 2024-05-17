from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites import requests
from django.http import request
from django.shortcuts import render, redirect, get_object_or_404

from canteen.models import *
from canteen.views import calculate_total_amount
from django.conf import settings


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

    return render(request, 'admin_panel/allItems.html', {'data': data, 'selected_category': category})


def get_username(user_id):
    url = f'{settings.API_URL}/customusers/{user_id}/'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data['username']
    else:
        return "Error occurred while fetching username"


from django.shortcuts import render
import requests


def get_delivery_status(last_order_id):
    url = f'{settings.API_URL}/orders/{last_order_id}/'
    response = requests.get(url)
    if response.status_code == 200:
        response_data = response.json()
        return response_data['delivery_status']
    else:
        return "Error occurred while fetching delivery status"


def get_remaining_orderdetails(last_order_id):
    url = f'{settings.API_URL}/orders/{last_order_id}/orderdetails/'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # print(data)
        filtered_data = [item for item in data if not item['isdelivered']]
        # #print(filtered_data)

        return filtered_data
    pass


@staff_member_required
def view_orders(request):
    # print("view_orders called")
    if request.method == 'GET':
        url = f'{settings.API_URL}/orders/remainingorders/'
        response = requests.get(url)

        pending_orders_data = []
        if response.status_code == 200:

            pending_orders = response.json()

            for order in pending_orders:
                print(order)
                if order['payment_status'] == "Pending":
                    continue
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
        return render(request, 'admin_panel/ManageOrders.html', context)

    elif request.method == 'POST':
        # Handle the AJAX request after marking an order as completed
        url = f'{settings.API_URL}/orders/remainingorders/'
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
            return JsonResponse({'success': False, 'error': 'Error occurred while fetching pending orders.'})

        return JsonResponse({'success': True, 'orders': pending_orders_data})


def change_order_status(order_id):
    url = f'{settings.API_URL}/orders/{order_id}/orderdetails/'
    response = requests.get(url)
    if response.status_code == 200:
        response_data = response.json()
        for data in response_data:
            if not data['isdelivered']:
                return False
        return True


from django.http import JsonResponse


@staff_member_required
def mark_order_completed(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        user_id = request.POST.get('user_id')
        order_detail_id = request.POST.get('order_detail_id')
        qty = request.POST.get('qty')

        url = f'{settings.API_URL}/orderdetails/{order_detail_id}/'
        data = {
            "order": order_id,
            "qty": qty,
            "isdelivered": True
        }
        response = requests.put(url, data=data)

        if change_order_status(order_id):
            url = f'{settings.API_URL}/orders/{order_id}/'
            data = {
                "delivery_status": "Delivered",
                "user": user_id
            }
            response = requests.put(url, data=data)

        if response.status_code == 200:
            # Fetch the updated orders data and return it as JSON response
            url = f'{settings.API_URL}/orders/remainingorders/'
            response = requests.get(url)

            pending_orders_data = []
            if response.status_code == 200:
                pending_orders = response.json()
                for order in pending_orders:
                    user_id = order['user']
                    last_order_id = order['id']
                    order_details = get_remaining_orderdetails(last_order_id)

                    total_amount = calculate_total_amount(order_details)

                    user_orders_data = []
                    for order_detail in order_details:
                        order_detail_data = {
                            'id': order_detail['id'],
                            'order': last_order_id,
                            'item': {
                                'id': order_detail['item']['id'],
                                'name': order_detail['item']['name'],
                                'price': order_detail['item']['price'],
                                'photo_url': order_detail['item']['photo_url']
                            },
                            'qty': order_detail['qty'],
                            'isdelivered': order_detail['isdelivered']
                        }
                        user_orders_data.append(order_detail_data)

                    pending_orders_data.append({
                        'order_id': last_order_id,
                        'user_name': get_username(user_id),
                        'user_id': user_id,
                        'total_amount': total_amount,
                        'orders': user_orders_data
                    })

            return JsonResponse({'success': True, 'orders': pending_orders_data})
        else:
            return JsonResponse({'success': False, 'error': 'Error updating order status'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
