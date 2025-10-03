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
    try:
        user = CustomUser.objects.get(id=user_id)
        return user.username
    except CustomUser.DoesNotExist:
        return "Unknown User"


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
    try:
        # Use select_related to avoid N+1 queries
        order_details = OrderDetails.objects.filter(
            order_id=last_order_id,
            isdelivered=False
        ).select_related('item').all()
        
        data = []
        for detail in order_details:
            data.append({
                'id': detail.id,
                'order': detail.order.id,
                'item': {
                    'id': detail.item.id,
                    'name': detail.item.name,
                    'price': float(detail.item.price),
                    'photo_url': detail.item.photo_url
                },
                'qty': detail.qty,
                'isdelivered': detail.isdelivered
            })
        return data
    except Exception as e:
        return []


@staff_member_required
def view_orders(request):
    if request.method == 'GET':
        try:
            # Get paid orders that are still pending delivery with optimized queries
            pending_orders = Orders.objects.filter(
                delivery_status='Pending',
                payment_status='Paid'
            ).select_related('user').prefetch_related(
                'order_details__item'
            ).all()

            pending_orders_data = []
            for order in pending_orders:
                # Get undelivered order details
                order_details = []
                total_amount = 0
                
                for detail in order.order_details.filter(isdelivered=False):
                    order_detail_data = {
                        'id': detail.id,
                        'order': order.id,
                        'item': {
                            'id': detail.item.id,
                            'name': detail.item.name,
                            'price': float(detail.item.price),
                            'photo_url': detail.item.photo_url
                        },
                        'qty': detail.qty,
                        'isdelivered': detail.isdelivered
                    }
                    order_details.append(order_detail_data)
                    total_amount += float(detail.item.price) * detail.qty

                if order_details:  # Only include orders with undelivered items
                    pending_orders_data.append({
                        'order_id': order.id,
                        'user_name': order.user.username,
                        'user_id': order.user.id,
                        'total_amount': total_amount,
                        'order_details': order_details
                    })

            context = {'orders': pending_orders_data}
            return render(request, 'admin_panel/ManageOrders.html', context)
            
        except Exception as e:
            messages.error(request, "Error occurred while fetching pending orders.")
            return redirect('admin_panel:view_orders')

    elif request.method == 'POST':
        # Handle the AJAX request after marking an order as completed
        try:
            pending_orders = Orders.objects.filter(
                delivery_status='Pending',
                payment_status='Paid'
            ).select_related('user').prefetch_related(
                'order_details__item'
            ).all()

            pending_orders_data = []
            for order in pending_orders:
                order_details = []
                total_amount = 0
                
                for detail in order.order_details.filter(isdelivered=False):
                    order_detail_data = {
                        'id': detail.id,
                        'order': order.id,
                        'item': {
                            'id': detail.item.id,
                            'name': detail.item.name,
                            'price': float(detail.item.price),
                            'photo_url': detail.item.photo_url
                        },
                        'qty': detail.qty,
                        'isdelivered': detail.isdelivered
                    }
                    order_details.append(order_detail_data)
                    total_amount += float(detail.item.price) * detail.qty

                if order_details:
                    pending_orders_data.append({
                        'order_id': order.id,
                        'user_name': order.user.username,
                        'user_id': order.user.id,
                        'total_amount': total_amount,
                        'order_details': order_details
                    })

            return JsonResponse({'success': True, 'orders': pending_orders_data})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'Error occurred while fetching pending orders.'})





from django.http import JsonResponse


@staff_member_required
def mark_order_completed(request):
    if request.method == 'POST':
        try:
            order_id = int(request.POST.get('order_id'))
            order_detail_id = int(request.POST.get('order_detail_id'))
            
            # Mark the specific order detail as delivered
            order_detail = OrderDetails.objects.get(id=order_detail_id)
            order_detail.isdelivered = True
            order_detail.save()
            
            # Check if all items in the order are delivered
            order = Orders.objects.get(id=order_id)
            remaining_items = OrderDetails.objects.filter(
                order=order, 
                isdelivered=False
            ).count()
            
            if remaining_items == 0:
                # All items delivered, mark order as delivered
                order.delivery_status = 'Delivered'
                order.save()
            
            # Get updated orders data
            pending_orders = Orders.objects.filter(
                delivery_status='Pending',
                payment_status='Paid'
            ).select_related('user').prefetch_related(
                'order_details__item'
            ).all()

            pending_orders_data = []
            for order in pending_orders:
                order_details = []
                total_amount = 0
                
                for detail in order.order_details.filter(isdelivered=False):
                    order_detail_data = {
                        'id': detail.id,
                        'order': order.id,
                        'item': {
                            'id': detail.item.id,
                            'name': detail.item.name,
                            'price': float(detail.item.price),
                            'photo_url': detail.item.photo_url
                        },
                        'qty': detail.qty,
                        'isdelivered': detail.isdelivered
                    }
                    order_details.append(order_detail_data)
                    total_amount += float(detail.item.price) * detail.qty

                if order_details:
                    pending_orders_data.append({
                        'order_id': order.id,
                        'user_name': order.user.username,
                        'user_id': order.user.id,
                        'total_amount': total_amount,
                        'orders': order_details
                    })

            return JsonResponse({'success': True, 'orders': pending_orders_data})
            
        except (OrderDetails.DoesNotExist, Orders.DoesNotExist, ValueError):
            return JsonResponse({'success': False, 'error': 'Order not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'An error occurred'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
