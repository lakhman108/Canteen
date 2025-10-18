from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites import requests
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import CustomUserLoginForm, CustomUserRegistrationForm
from .models import CustomUser, Orders, Payment, OrderDetails, FoodDetails
import razorpay
import logging

logger = logging.getLogger(__name__)


@login_required
def filteritems(request):
    category = request.POST.get('category')

    if category == 'all':
        raw_data = FoodDetails.objects.all().order_by('id')
    else:
        raw_data = FoodDetails.objects.filter(food__name=category).order_by('food_id')

    data = []
    for item in raw_data:
        data.append({'id': item.id, 'name': item.name, 'stock_qty': item.stock_qty, 'price': item.price,
                     'photo_url': item.photo_url,
                     'rating':item.rating})

    return render(request, 'index.html', {'data': data})


@login_required
def contact(request):
    return HttpResponse('Contact page')

@login_required
def index(request):
    try:
        logger.info(f"Index view called - User: {request.user}, Method: {request.method}")
        logger.info(f"Request path: {request.path}")
        
        # Test database connection
        logger.info("Attempting to query FoodDetails...")
        raw_data = FoodDetails.objects.all().order_by('id')
        logger.info(f"Found {raw_data.count()} food items")
        
        data = []
        for item in raw_data:
            data.append({'id': item.id, 'name': item.name, 'stock_qty': item.stock_qty, 'price': item.price,
                         'photo_url': item.photo_url,
                         'rating': item.rating})

        logger.info(f"Prepared data for {len(data)} items")
        logger.info("Attempting to render index.html template...")
        
        return render(request, 'index.html', {'data': data})
        
    except Exception as e:
        logger.error(f"Error in index view: {str(e)}", exc_info=True)
        from django.http import HttpResponse
        return HttpResponse(f"Error in index view: {str(e)}", status=500)


from django.shortcuts import render


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
    try:
        # Get the latest order for the user that's still pending
        order = Orders.objects.filter(
            user_id=user_id, 
            delivery_status='Pending'
        ).order_by('-id').first()
        
        if order:
            return order.id
        else:
            return "No order found"
    except Exception as e:
        return "No order found"


def get_orderdetails(order_id):
    try:
        # Use select_related to avoid N+1 queries
        order_details = OrderDetails.objects.filter(
            order_id=order_id,
            isdelivered=False  # Only get undelivered items
        ).select_related('item', 'order').all()
        
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


def calculate_total_amount(order_details):
    total_amount = 0
    for detail in order_details:
        item = detail['item']
        total_amount += item['price'] * detail['qty']
    return total_amount


def get_cart_data(user_id):
    try:
        # Direct query with select_related to avoid N+1 queries
        # Only get undelivered items from pending orders
        order_details = OrderDetails.objects.filter(
            order__user_id=user_id,
            order__delivery_status='Pending',
            isdelivered=False
        ).select_related('item', 'order').all()
        
        cart_data = []
        for detail in order_details:
            cart_data.append({
                'order_details_id': detail.id,
                'food_id': detail.item.id,
                'food_name': detail.item.name,
                'price': float(detail.item.price),
                'image_url': detail.item.photo_url,
                'quantity': detail.qty,
                'total_price': float(detail.item.price) * detail.qty,
            })
        
        return cart_data
    except Exception as e:
        return []


def cart(request):
    cart_data = []
    user_id = request.user.id

    if request.method != 'POST':

        cart_data = get_cart_data(user_id)



        return render(request, 'cart.html', {'cart_data': cart_data})
    else:
        try:
            item_id = int(request.POST['item_id'])
            qty = 1
            
            # Check if item exists and has enough stock
            food_item = FoodDetails.objects.get(id=item_id)
            if food_item.stock_qty < qty:
                return HttpResponse({'message': 'Not enough stock'})
            
            # Get or create pending order
            order, created = Orders.objects.get_or_create(
                user_id=user_id,
                delivery_status='Pending',
                defaults={'payment_status': 'Pending'}
            )
            
            # Check if item already in cart
            order_detail, created = OrderDetails.objects.get_or_create(
                order=order,
                item_id=item_id,
                defaults={'qty': qty, 'isdelivered': False}
            )
            
            if not created:
                # Item already exists, update quantity
                order_detail.qty += qty
                order_detail.save()
            
            # Update stock
            food_item.stock_qty -= qty
            food_item.save()
            
            return HttpResponse({'message': 'Item added to cart successfully'})
            
        except FoodDetails.DoesNotExist:
            return HttpResponse({'error': 'Item not found'})
        except Exception as e:
            return HttpResponse({'error': 'An error occurred'})


def about(request):
    return render(request, "about.html");


def contact(request):
    return render(request, "contact.html");


def remove_order_detail(request, order_detail_id):
    try:
        order_detail = OrderDetails.objects.get(id=order_detail_id)
        
        # Restore stock
        food_item = order_detail.item
        food_item.stock_qty += order_detail.qty
        food_item.save()
        
        # Delete order detail
        order_detail.delete()
        
    except OrderDetails.DoesNotExist:
        pass
    
    return redirect('canteen:cart')


def update_order_detail_quantity(request, order_detail_id, action):
    try:
        order_detail = OrderDetails.objects.get(id=order_detail_id)
        food_item = order_detail.item
        
        if action == 'add':
            # Check stock availability
            if food_item.stock_qty < 1:
                messages.error(request, 'Not enough stock available')
                return redirect('canteen:cart')
            
            order_detail.qty += 1
            food_item.stock_qty -= 1
            
        elif action == 'decrease':
            if order_detail.qty <= 1:
                # Remove item completely and restore stock
                food_item.stock_qty += order_detail.qty
                food_item.save()
                order_detail.delete()
                return redirect('canteen:cart')
            else:
                order_detail.qty -= 1
                food_item.stock_qty += 1
        else:
            return redirect('canteen:cart')
        
        order_detail.save()
        food_item.save()
        
    except OrderDetails.DoesNotExist:
        pass
    
    return redirect('canteen:cart')


# def payment(request):
#     print("payment called\n")
#     #print("function of payment called")
#     user_id = request.session['user_id']
#     order_id = get_order_id(user_id)
#     order_details = get_orderdetails(order_id)
#     total_amount = calculate_total_amount(order_details)
#
#     client = razorpay.Client(auth=("rzp_test_JTePD1c5RLT3nj", "7p5e6T5NGyUl4fgOJAYYIzze"))
#     total_amount *= 100
#     data = {"amount": total_amount, "currency": "INR", "receipt": "order_rcptid_11"}
#     payment = client.order.create(data=data)
#     payment_data = {
#         'user': user_id,
#         'order': order_id,
#         'razorpay_order_id': payment['id'],
#     }
#
#     url = f'{settings.API_URL}/payment/'
#     response = requests.post(url, data=payment_data)
#     # if response.status_code == 201:
#         #print("Payment created successfully")
#     #print(response.status_code)
#     #print(response.json())
#
#
#     return render(request, 'payment.html', {'amount': total_amount})


def payment(request):
    #print("function of payment called")
    try:
        user_id = request.user.id
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
        #print(f"Error occurred while creating Razorpay payment: {e}")
        messages.error(request, "Error occurred while creating Razorpay payment.")
        return redirect('canteen:index')

    try:
        # Create or update payment record directly
        order_obj = Orders.objects.get(id=order_id)
        payment_obj, created = Payment.objects.get_or_create(
            order=order_obj,
            defaults={
                'amount': total_amount / 100,  # Convert back from paisa to rupees
                'razorpay_order_id': payment['id']
            }
        )
        
        if not created:
            payment_obj.amount = total_amount / 100
            payment_obj.razorpay_order_id = payment['id']
            payment_obj.save()
            
    except Orders.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('canteen:index')
    except Exception as e:
        messages.error(request, "Error occurred while creating payment.")

    #print(response.status_code)
    #print(response.json())

    return render(request, 'payment.html', {'amount': total_amount})


# ... (other functions)

def get_waiting_list_id():
    orders = Orders.objects.filter(payment_status='Paid', delivery_status='Pending').order_by('id')

    x = 0;
    for order in orders:
        x += 1

    return x;


def sucess(request):
    try:
        razorpay_payment_id = request.GET.get('razorpay_payment_id', '')
        razorpay_order_id = request.GET.get('razorpay_order_id', '')
        razorpay_signature = request.GET.get('razorpay_signature', '')
    except Exception as e:
        # Handle exceptions related to GET parameters
        #print(f"Error occurred while retrieving GET parameters: {e}")
        messages.error(request, "Error occurred while retrieving GET parameters.")
        return redirect('canteen:index')

    try:
        user_id = request.user.id
    except KeyError:
        # Handle the case when user_id is not in the session
        messages.error(request, "User ID not found in the session.")
        return redirect('canteen:index')

    try:
        order_id = get_order_id(user_id)
        if order_id == "No order found":
            messages.error(request, "Order not found.")
            return redirect('canteen:index')
            
        # Update payment details
        order_obj = Orders.objects.get(id=order_id)
        payment_obj = Payment.objects.get(order=order_obj)
        
        payment_obj.razorpay_payment_id = razorpay_payment_id
        payment_obj.razorpay_order_id = razorpay_order_id
        payment_obj.razorpay_signature = razorpay_signature
        payment_obj.save()
        
        # Update order status to paid
        order_obj.payment_status = 'Paid'
        order_obj.save()
        
    except (Orders.DoesNotExist, Payment.DoesNotExist):
        messages.error(request, "Order or payment not found.")
        return redirect('canteen:index')
    except Exception as e:
        messages.error(request, "Error occurred while updating payment details.")

    return render(request, 'OrderStatus.html', {'waiting_list_id': get_waiting_list_id()})


