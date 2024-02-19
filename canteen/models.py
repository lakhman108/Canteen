from django.contrib.auth.models import AbstractUser
from django.db import models



class CustomUser(AbstractUser):
    mobile_number = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        # Specify the app_label to avoid conflicts with the built-in User model
        app_label = 'canteen'

# Set custom related_name for groups and user_permissions
CustomUser._meta.get_field('groups').remote_field.related_name = 'customuser_set'
CustomUser._meta.get_field('user_permissions').remote_field.related_name = 'customuser_set'

class Orders(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    payment_status = models.CharField(max_length=255, unique=True)
    delivery_status = models.CharField(max_length=255)

class OrderDetails(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    item_id = models.IntegerField()
    qty = models.IntegerField()

class Payment(models.Model):
    order = models.OneToOneField(Orders, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=4, default=0.0000)
    payment_status = models.ForeignKey(Orders, to_field='payment_status', on_delete=models.CASCADE, related_name='payments')

class Food(models.Model):
    name = models.CharField(max_length=255)

class FoodDetails(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    stock_qty = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    photo_url = models.CharField(max_length=255,default=None)
