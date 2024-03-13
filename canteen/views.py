from urllib.request import HTTPRedirectHandler
from django.contrib.auth import authenticate, login
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

def get_last_order(user_id):
    try:
        # Get the latest order for the user
        last_order = Orders.objects.filter(user_id=user_id).latest('id')
        return last_order
    except Orders.DoesNotExist:
        # Handle the case where no orders exist for the user
        return None  # Return None instead of a string

def items_exits_in_last_order(order_id, food_id):
    try:
        # Check if the item exists in the order
        return OrderDetails.objects.get(order_id=order_id, item_id=food_id)
    except OrderDetails.DoesNotExist:
        # Handle the case where the item is not found in the order
        return None  # Return None instead of a string

def cart(request):
    alert = ""
    cart_data = []
    if request.method == 'POST':
        food_id = request.POST.get('item_id')
        user_id = request.session.get('user_id')

        last_order = get_last_order(user_id)
        if last_order is None:
            order = Orders(user_id=user_id, payment_status='Pending', delivery_status='Pending')
            order.save()
        else:
            order = last_order

        # Check if the item exists in the last order
        order_detail = items_exits_in_last_order(order.id, food_id)
        if order_detail is not None:
            # If the item exists, increment its quantity
            order_detail.qty += 1
            order_detail.save()
        else:
            # If the item does not exist, create a new OrderDetails instance
            order_detail = OrderDetails(order=order, item_id=food_id, qty=1)
            order_detail.save()

        alert = "Added to cart"
        return HttpResponseRedirect(reverse('canteen:index'))

    user_orders = Orders.objects.filter(user_id=request.session.get('user_id'))
    for order in user_orders:
        order_details = OrderDetails.objects.filter(order=order)
        for detail in order_details:
            food = FoodDetails.objects.get(id=detail.item_id)
            cart_data.append({
                'food_id': food.id,
                'food_name': food.name,
                'quantity': detail.qty,
                'price': food.price,
                'image_url': food.photo_url,
                'total_price': food.price * detail.qty
            })

    return render(request, 'cart.html', {'alert': alert, 'cart_data': cart_data})


def about(request):
    return render(request,"about.html");

def contact(request):
    return render(request,"contact.html");