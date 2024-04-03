from rest_framework import serializers
from canteen.models import CustomUser, Orders, Food, FoodDetails, OrderDetails, Payment


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = '__all__'


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = '__all__'


class FoodDetailsRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        food_details = FoodDetails.objects.get(pk=value.pk)
        return {
            'id': food_details.id,
            'name': food_details.name,
            'price': food_details.price,
            'photo_url': food_details.photo_url,

            # 'url': f'https://www.canteenmanagement.live/api/fooddetails/{food_details.id}/'  # Include the item URL here
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
