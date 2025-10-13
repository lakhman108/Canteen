from rest_framework import serializers
from canteen.models import CustomUser, Orders, Food, FoodDetails, OrderDetails, Payment


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


class OrdersSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Orders
        fields = '__all__'


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = '__all__'


class FoodDetailsRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        # No need for additional query since value is already the FoodDetails object
        return {
            'id': value.id,
            'name': value.name,
            'price': value.price,
            'photo_url': value.photo_url,
            # 'url': f'http://localhost:8000/api/fooddetails/{value.id}/'  # Include the item URL here
        }


class FoodDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodDetails
        fields = '__all__'


class OrderDetailsSerializer(serializers.ModelSerializer):
    item = FoodDetailsRelatedField(read_only=True)
    
    class Meta:
        model = OrderDetails
        fields = ['id', 'order', 'item', 'qty', 'isdelivered']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'