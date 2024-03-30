from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites import requests
from django.shortcuts import render, redirect

from .forms import CustomUserLoginForm, CustomUserRegistrationForm
from .models import CustomUser
from .models import FoodDetails
import razorpay


@login_required
def contact(request):
    return HttpResponse('Contact page')


@login_required
def index(request):
    raw_data = FoodDetails.objects.all()
    data = []
    for item in raw_data:
        data.append({'id': item.id, 'name': item.name, 'stock_qty': item.stock_qty, 'price': item.price,
                     'photo_url': item.photo_url})

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
            email = username + "@gmail.com"  # Get email from the form

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


import requests
from django.http import HttpResponse


def get_order_id(user_id):
    url = f'http://localhost:8000/api/customusers/{user_id}/orders/'

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if (data == []):
            return "No order found"
        order_id = data[0]['id']
        return order_id
    else:
        return "No order found"


def get_orderdetails(order_id):
    url = f'http://localhost:8000/api/orders/{order_id}/orderdetails/'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return "No order details found"


def calculate_total_amount(order_details):
    total_amount = 0
    for detail in order_details:
        item = detail['item']
        total_amount += item['price'] * detail['qty']
    return total_amount


def get_cart_data(user_id):
    cart_data = []
    order_id = get_order_id(user_id)
    if(order_id == "No order found"):

        return cart_data
    order_details_response = get_orderdetails(order_id)

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
    return render(request, "about.html");


def contact(request):
    return render(request, "contact.html");


def remove_order_detail(request, order_detail_id):
    url = f'http://localhost:8000/api/orderdetails/{order_detail_id}/'
    response = requests.delete(url)

    if response.status_code == 204:
        # OrderDetails object successfully deleted
        return redirect('canteen:cart')
    else:
        # Handle the error case
        return redirect('canteen:cart')


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


def payment(request):

    print("function of payment called")
    user_id = request.session['user_id']
    order_id = get_order_id(user_id)
    order_details = get_orderdetails(order_id)
    total_amount = calculate_total_amount(order_details)

    client = razorpay.Client(auth=("rzp_test_JTePD1c5RLT3nj", "7p5e6T5NGyUl4fgOJAYYIzze"))
    total_amount *= 100
    data = {"amount": total_amount, "currency": "INR", "receipt": "order_rcptid_11"}
    payment = client.order.create(data=data)
    payment_data = {
        'user': user_id,
        'order': order_id,
        'razorpay_order_id': payment['id'],
    }

    url = f'http://localhost:8000/api/payment/'
    response = requests.post(url, data=payment_data)
    if response.status_code == 201:
        print("Payment created successfully")
    print(response.status_code)
    print(response.json())


    return render(request, 'payment.html', {'amount': total_amount})


def payment(request):
    print("function of payment called")
    try:
        user_id = request.session['user_id']
    except KeyError:
        # Handle the case when user_id is not in the session
        messages.error(request, "User ID not found in the session.")
        return redirect('canteen:index')

    order_id = get_order_id(user_id)
    if order_id == "No order found" or order_id == "Error occurred while fetching order ID":
        messages.error(request, order_id)
        return redirect('canteen:index')

    order_details = get_orderdetails(order_id)
    if order_details == "Error occurred while fetching order details":
        messages.error(request, order_details)
        return redirect('canteen:index')

    total_amount = calculate_total_amount(order_details)

    try:
        client = razorpay.Client(auth=("rzp_test_JTePD1c5RLT3nj", "7p5e6T5NGyUl4fgOJAYYIzze"))
        total_amount *= 100
        data = {"amount": total_amount, "currency": "INR", "receipt": "order_rcptid_11"}
        payment = client.order.create(data=data)
    except Exception as e:
        # Handle exceptions related to Razorpay payment
        print(f"Error occurred while creating Razorpay payment: {e}")
        messages.error(request, "Error occurred while creating Razorpay payment.")
        return redirect('canteen:index')

    payment_data = {
        'user': user_id,
        'order': order_id,
        'razorpay_order_id': payment['id'],
    }

    try:
        url = f'http://localhost:8000/api/payment/'
        response = requests.post(url, data=payment_data)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        if response.status_code == 201:
            print("Payment created successfully")
    except requests.exceptions.RequestException as e:
        # Handle exceptions related to the HTTP request
        print(f"Error occurred while creating payment: {e}")
        messages.error(request, "Error occurred while creating payment.")

    print(response.status_code)
    print(response.json())

    return render(request, 'payment.html', {'amount': total_amount})

# ... (other functions)

def sucess(request):
    try:
        razorpay_payment_id = request.GET.get('razorpay_payment_id', '')
        razorpay_order_id = request.GET.get('razorpay_order_id', '')
        razorpay_signature = request.GET.get('razorpay_signature', '')
    except Exception as e:
        # Handle exceptions related to GET parameters
        print(f"Error occurred while retrieving GET parameters: {e}")
        messages.error(request, "Error occurred while retrieving GET parameters.")
        return redirect('canteen:index')

    try:
        user_id = request.session['user_id']
    except KeyError:
        # Handle the case when user_id is not in the session
        messages.error(request, "User ID not found in the session.")
        return redirect('canteen:index')

    payment_data = {
        'user': user_id,
        'order': get_order_id(user_id),
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_signature': razorpay_signature,
    }

    try:
        url = f'http://localhost:8000/api/payment/{get_order_id(user_id)}/paymentdeatils/'
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-2xx status codes

        if response.status_code == 200:
            data = response.json()
            payment_id = data[0]['id']
            url = f'http://localhost:8000/api/payment/{payment_id}/'
            response = requests.put(url, data=payment_data)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            print(data)
    except requests.exceptions.RequestException as e:
        # Handle exceptions related to the HTTP request
        print(f"Error occurred while updating payment details: {e}")
        messages.error(request, "Error occurred while updating payment details.")

    try:
        url = f'http://localhost:8000/api/orders/{get_order_id(user_id)}/'
        data = {
            "payment_status": "Paid",
            "user": user_id
        }
        response = requests.put(url, data=data)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        print(response.json())
    except requests.exceptions.RequestException as e:
        # Handle exceptions related to the HTTP request
        print(f"Error occurred while updating order status: {e}")
        messages.error(request, "Error occurred while updating order status.")

    return HttpResponse("Payment Successfull")