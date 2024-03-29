from urllib.request import HTTPRedirectHandler
from django.contrib.auth import authenticate, login
from django.contrib.sites import requests
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect ,HttpResponse
from django.contrib.auth.decorators import login_required

from .forms import CustomUserLoginForm, CustomUserRegistrationForm
from .models import CustomUser

from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout
from django.http import Http404, HttpResponseRedirect
from .models import Food, FoodDetails,Orders,OrderDetails,Payment
from django.urls import reverse

@login_required
def contact(request):
    return HttpResponse('Contact page')
   

@login_required
def index(request):
    raw_data = FoodDetails.objects.all()
    data = []
    for item in raw_data:
        data.append({'id': item.id, 'name': item.name, 'stock_qty': item.stock_qty, 'price': item.price, 'photo_url': item.photo_url})
        
        # print(item.name)
    # print(data)
    # print(request.user)
    # print(request.GET.get('next'))

   
    return render(request, 'index.html', {'data': data})

def custom_user_login(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Authenticate the user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Log in the user
                request.session['user_id'] = user.id
                login(request, user)
                return redirect('canteen:index')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid form data.')
    else:
        form = CustomUserLoginForm()

    return render(request, 'login.html', {'form': form})

def custom_user_register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            email = username+"@gmail.com"  # Get email from the form

            # Create the user using create_user method
            user = CustomUser.objects.create_user(username, email, password)

            # Log in the user
            login(request, user)
            request.session['user_id'] = user.id
            return redirect('canteen:index')
        else:
            messages.error(request, 'Invalid form data.')
    else:
        form = CustomUserRegistrationForm()

    return render(request, 'register.html', {'form': form})




def custom_user_logout(request):
    logout(request)
    # Redirect to a non-protected page
    return redirect('canteen:index')


def show_items(request):
    return HttpResponse('Items page');

# def cart(request):
#     alert = ""
#     if request.method == 'POST':
#         # print(request.POST)
#         food_id = request.POST.get('item_id')
#         # qty = request.POST.get('qty')
#         print(food_id)
#         alert+="Added to cart"
#         print(alert)
#         # print(qty)
#         # food = Food.objects.get(id=food_id)
#         # food_details = FoodDetails.objects.get(id=food_id)
#         # print(food)
#         # print(food_details)
#         # print(food_details.stock_qty)
#         # print(food_details.stock_qty - int(qty))
#         # if food_details.stock_qty - int(qty) < 0:
#         #     return HttpResponse('Not enough stock')
#         # else:
#         #     food_details.stock_qty = food_details.stock_qty - int(qty)
#         #     food_details.save()
#         #     return HttpResponse('Added to cart')
#         return HttpResponseRedirect(reverse("canteen:index"),{'alert':alert})
#     return render(request, 'cart.html',{'alert':alert});

import requests
from django.http import HttpResponse



def get_cart_data(user_id):
    cart_data=[]
    url = f'http://localhost:8000/api/customusers/{user_id}/orders/'

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        order_id = data[0]['id']
        print(order_id)
        url = f'http://localhost:8000/api/orders/{order_id}/orderdetails/'
        order_details_response = requests.get(url)
        if response.status_code == 200:
            order_details_response = order_details_response.json()

        for detail in order_details_response:
            item = detail['item']
            cart_data.append({
                'order_details_id': detail['id'],  # This is the order details ID, not the item ID
                'food_id': item['id'],
                'food_name': item['name'],
                'price': item['price'],
                'image_url': item['photo_url'],
                'quantity': detail['qty'],
                'total_price': item['price'] * detail['qty'],
            })

        return cart_data;
def cart(request):
    cart_data = []
    user_id = request.session['user_id']

    if request.method != 'POST':

        cart_data = get_cart_data(user_id)


        # Process the data as needed
        return render(request, 'cart.html', {'cart_data': cart_data})
    else:
        item_id = request.POST['item_id']

        url = f'http://localhost:8000/api/orderdetails/'
        data = {
            'user': int(user_id),
            'item': int(item_id),
            'qty': int(1),
        }
        response = requests.post(url, data=data)


        return redirect('canteen:index')
def about(request):
    return render(request,"about.html");

def contact(request):
    return render(request,"contact.html");


def remove_order_detail(request, order_detail_id):
    url = f'http://localhost:8000/api/orderdetails/{order_detail_id}/'
    response = requests.delete(url)

    if response.status_code == 204:
        # OrderDetails object successfully deleted
        return redirect('canteen:cart')
    else:
        # Handle the error case
        return redirect('canteen:cart')



# views.py
import requests
from django.shortcuts import render, redirect

def update_order_detail_quantity(request, order_detail_id, action):
    url = f'http://localhost:8000/api/orderdetails/{order_detail_id}/'

    if action == 'add':
        quantity_change = 1
    elif action == 'decrease':
        quantity_change = -1
    else:
        return redirect('canteen:cart')  # Invalid action, redirect to cart view

    # Get the current order detail data
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        order_id = data['order']
        new_quantity = data['qty'] + quantity_change

        if new_quantity < 1:
            # If the new quantity is less than 1, delete the order detail
            requests.delete(url)
        else:
            # Update the order detail quantity
            payload = {
                'order': order_id,
                'qty': new_quantity
            }
            requests.put(url, json=payload)

    return redirect('canteen:cart')