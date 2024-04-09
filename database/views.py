

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from database.serializers import CustomUserSerializer, OrdersSerializer
from canteen.models import CustomUser, Orders, Food, FoodDetails, OrderDetails, Payment
from .serializers import *


def get_last_order(user_id):
    orders = Orders.objects.filter(user_id=user_id).order_by('-id')
    return orders[0] if orders else None


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated access

    # customuser/{user_id}/orders
    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        user = CustomUser.objects.get(pk=pk)
        orders = Orders.objects.filter(user=user).order_by('-id')
        permission_classes = [AllowAny]  # Allow unauthenticated access
        user_orders = OrdersSerializer(orders, many=True, context={'request': request})
        return Response(user_orders.data)

        pass


from rest_framework import status


class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated access

    @action(detail=True, methods=['get'])
    def orderdetails(self, request, pk=None):
        order = Orders.objects.get(pk=pk)
        order_details = OrderDetails.objects.filter(order=order)
        order_details = OrderDetailsSerializer(order_details, many=True, context={'request': request})
        return Response(order_details.data)

    def create(self, request):

        user_id = request.data['user']  # Get the authenticated user's ID
        last_order = Orders.objects.filter(user_id=user_id).order_by('-id')

        if not last_order or last_order.delivery_status != 'Pending':
            order = Orders(user_id=user_id, delivery_status='Pending', payment_status='Pending')
            order.save()
            return Response({'message': 'New order created.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Last order is still pending.'}, status=status.HTTP_200_OK)
    @action(detail=False, methods=['get'])
    def remainingorders(self, request):
        pending_orders = Orders.objects.filter(delivery_status='Pending')
        serializer = self.get_serializer(pending_orders, many=True)
        return Response(serializer.data)


class FoodViewSet(viewsets.ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated access


class FoodDetailsViewSet(viewsets.ModelViewSet):
    queryset = FoodDetails.objects.all()
    serializer_class = FoodDetailsSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated access

    @action(detail=False, methods=['POST'])
    def additem(self, request):
        name = request.data['name']
        price = request.data['price']
        photo_url = request.data['photo_url']
        stock_qty = request.data['stock_qty']
        food=request.data['food']

        food=Food.objects.get(id=food)
        fooddetails=FoodDetails.objects.create(name=name,price=price,photo_url=photo_url,stock_qty=stock_qty,food=food)

        fooddetails.save()
        fooddetails_serializer = FoodDetailsSerializer(fooddetails)
        return Response(fooddetails_serializer.data, status=status.HTTP_201_CREATED)




from rest_framework import viewsets, status
from rest_framework.response import Response
from canteen.models import CustomUser, Orders, FoodDetails, OrderDetails


class OrderDetailsViewSet(viewsets.ModelViewSet):
    queryset = OrderDetails.objects.all()
    serializer_class = OrderDetailsSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated access

    def create(self, request):
        user_id = request.data['user']
        item_id = request.data['item']
        qty = request.data['qty']

        # Get the latest order for the user
        order = Orders.objects.filter(user_id=user_id).order_by('-id').first()

        item_qty = FoodDetails.objects.get(id=item_id).stock_qty
        item_qty = int(item_qty)
        qty = int(qty)
        if qty > item_qty:
            return Response({'message': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)

        if not order or order.delivery_status != 'Pending':
            # If there is no order, create a new one
            order = Orders.objects.create(user_id=user_id, delivery_status='Pending', payment_status='Pending')

        # Check if the item already exists in the order details
        order_detail = OrderDetails.objects.filter(order=order, item_id=item_id).first()
        food_details = FoodDetails.objects.get(id=item_id)

        food_details.stock_qty -= qty
        food_details.save()

        if order_detail:
            # If the item already exists, update the quantity
            order_detail.qty += qty

            order_detail.save()

            return Response({'message': 'Item quantity updated in cart.'}, status=status.HTTP_200_OK)
        else:
            # If the item doesn't exist, create a new order detail
            order_detail = OrderDetails.objects.create(order=order, item_id=item_id, qty=qty)
            return Response({'message': 'Item added to cart.'}, status=status.HTTP_201_CREATED)





from rest_framework import viewsets, status
from rest_framework.response import Response
from canteen.models import Orders, OrderDetails, Payment


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated access

    # print("PaymentViewSet")
    @action(detail=True, methods=['get'])
    def paymentdeatils(self, request, pk=None):
        order = Orders.objects.get(pk=pk)
        payment_details = Payment.objects.filter(order=order)

        payment_details = PaymentSerializer(payment_details, many=True, context={'request': request})
        return Response(payment_details.data)

    def create(self, request):
        user_id = request.data['user']
        order_id = request.data['order']

        order = Orders.objects.get(id=order_id)
        order_details = OrderDetails.objects.filter(order=order)
        total_amount = 0
        for order_detail in order_details:
            total_amount += order_detail.item.price * order_detail.qty

        # Check if a Payment instance already exists for the order
        payment = Payment.objects.filter(order=order).first()

        if payment:
            # If a Payment instance exists, update its amount
            payment.amount = total_amount
            payment.save()
        else:
            # If no Payment instance exists, create a new one
            payment = Payment.objects.create(order=order, amount=total_amount)

        # Processing payment
        order.payment_status = 'Pending'
        order.save()

        # Serialize the payment instance
        payment_serializer = PaymentSerializer(payment)
        data = {
            'payment': payment_serializer.data,
            'message': 'Payment processed successfully.'
        }
        return Response(data, status=status.HTTP_201_CREATED)