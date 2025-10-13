from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomUserViewSet, OrdersViewSet, FoodViewSet, 
    FoodDetailsViewSet, OrderDetailsViewSet, PaymentViewSet
)

router = DefaultRouter()
router.register(r'customuser', CustomUserViewSet)
router.register(r'orders', OrdersViewSet)
router.register(r'food', FoodViewSet)
router.register(r'fooddetails', FoodDetailsViewSet)
router.register(r'orderdetails', OrderDetailsViewSet)
router.register(r'payment', PaymentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]