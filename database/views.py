from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from canteen.models import CustomUser, Orders, Food, FoodDetails, OrderDetails, Payment
from .serializers import (
    CustomUserSerializer, OrdersSerializer, FoodSerializer, 
    FoodDetailsSerializer, OrderDetailsSerializer, PaymentSerializer
)


def get_last_order(user_id):
    return Orders.objects.filter(user_id=user_id).select_related('user').order_by('-id').first()


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated access

    # customuser/{user_id}/orders
    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        try:
            user = CustomUser.objects.get(pk=pk)
            # Only get pending orders to avoid showing delivered orders in cart
            orders = Orders.objects.filter(user=user, delivery_status='Pending').select_related('user').order_by('-id')
            user_orders = OrdersSerializer(orders, many=True, context={'request': request})
            return Response(user_orders.data)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated access

    @action(detail=True, methods=['get'])
    def orderdetails(self, request, pk=None):
        try:
            order = Orders.objects.get(pk=pk)
            # Use select_related to avoid N+1 queries for item and food relationships
            order_details = OrderDetails.objects.filter(order=order).select_related('item', 'item__food')
            serializer = OrderDetailsSerializer(order_details, many=True, context={'request': request})
            return Response(serializer.data)
        except Orders.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        try:
            user_id = request.data['user']
            # Check if there's already a pending order
            last_order = Orders.objects.filter(user_id=user_id, delivery_status='Pending').order_by('-id').first()
            
            if not last_order:
                order = Orders.objects.create(user_id=user_id, delivery_status='Pending', payment_status='Pending')
                return Response({'message': 'New order created.'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Last order is still pending.'}, status=status.HTTP_200_OK)
        except KeyError:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def remainingorders(self, request):
        # Only get paid orders that are pending delivery
        pending_orders = Orders.objects.filter(
            delivery_status='Pending',
            payment_status='Paid'
        ).select_related('user').prefetch_related('order_details__item')
        serializer = self.get_serializer(pending_orders, many=True)
        return Response(serializer.data)


class FoodViewSet(viewsets.ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated access


class FoodDetailsViewSet(viewsets.ModelViewSet):
    queryset = FoodDetails.objects.select_related('food').all()
    serializer_class = FoodDetailsSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated access

    @action(detail=False, methods=['POST'])
    def additem(self, request):
        try:
            name = request.data['name']
            price = request.data['price']
            photo_url = request.data['photo_url']
            stock_qty = request.data['stock_qty']
            food_id = request.data['food']

            # Check if the Food object exists
            try:
                food = Food.objects.get(id=food_id)
            except Food.DoesNotExist:
                return Response(
                    {'error': f'Food with id {food_id} does not exist'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create the food item without specifying ID (let Django auto-generate)
            fooddetails = FoodDetails.objects.create(
                name=name,
                price=price,
                photo_url=photo_url,
                stock_qty=stock_qty,
                food=food
            )
            fooddetails_serializer = FoodDetailsSerializer(fooddetails)
            return Response(fooddetails_serializer.data, status=status.HTTP_201_CREATED)
            
        except KeyError as e:
            return Response(
                {'error': f'Missing required field: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Handle database integrity errors
            return Response(
                {'error': f'Database error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderDetailsViewSet(viewsets.ModelViewSet):
    queryset = OrderDetails.objects.select_related('order', 'item', 'item__food').all()
    serializer_class = OrderDetailsSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated access

    def create(self, request):
        try:
            user_id = request.data['user']
            item_id = request.data['item']
            qty = int(request.data['qty'])

            # Get the latest pending order for the user
            order = Orders.objects.filter(user_id=user_id, delivery_status='Pending').order_by('-id').first()

            # Check stock availability
            try:
                food_details = FoodDetails.objects.get(id=item_id)
            except FoodDetails.DoesNotExist:
                return Response({'error': 'Item not found'}, status=status.HTTP_400_BAD_REQUEST)

            if qty > food_details.stock_qty:
                return Response({'message': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)

            # Create order if none exists
            if not order:
                order = Orders.objects.create(user_id=user_id, delivery_status='Pending', payment_status='Pending')

            # Check if the item already exists in the order details
            order_detail = OrderDetails.objects.filter(order=order, item_id=item_id, isdelivered=False).first()

            # Update stock
            food_details.stock_qty -= qty
            food_details.save()

            if order_detail:
                # If the item already exists, update the quantity
                order_detail.qty += qty
                order_detail.save()
                return Response({'message': 'Item quantity updated in cart.'}, status=status.HTTP_200_OK)
            else:
                # If the item doesn't exist, create a new order detail
                order_detail = OrderDetails.objects.create(
                    order=order, 
                    item_id=item_id, 
                    qty=qty,
                    isdelivered=False
                )
                return Response({'message': 'Item added to cart.'}, status=status.HTTP_201_CREATED)
        except KeyError as e:
            return Response(
                {'error': f'Missing required field: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('order', 'order__user').all()
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated access

    @action(detail=True, methods=['get'])
    def paymentdeatils(self, request, pk=None):
        try:
            order = Orders.objects.select_related('user').get(pk=pk)
            payment_details = Payment.objects.filter(order=order).select_related('order')
            serializer = PaymentSerializer(payment_details, many=True, context={'request': request})
            return Response(serializer.data)
        except Orders.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        try:
            user_id = request.data['user']
            order_id = request.data['order']
            order = Orders.objects.get(id=order_id)

            # Use select_related to avoid N+1 queries
            order_details = OrderDetails.objects.filter(order=order, isdelivered=False).select_related('item', 'item__food')
            
            total_amount = 0
            for order_detail in order_details:
                total_amount += order_detail.item.price * order_detail.qty

            # Check if a Payment instance already exists for the order
            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={'amount': total_amount}
            )
            
            if not created:
                # If a Payment instance exists, update its amount
                payment.amount = total_amount
                payment.save()

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
        except Orders.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except KeyError as e:
            return Response(
                {'error': f'Missing required field: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)