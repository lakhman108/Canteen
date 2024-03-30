from django.contrib.auth.models import AbstractUser
from django.db import models


from django.utils import timezone
class CustomUser(AbstractUser):
    mobile_number = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        app_label = 'canteen'

    def __str__(self):
        return self.username + ' - ' + self.email

CustomUser._meta.get_field('groups').remote_field.related_name = 'customuser_set'
CustomUser._meta.get_field('user_permissions').remote_field.related_name = 'customuser_set'





class Orders(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    # created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=255, choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')
    delivery_status = models.CharField(max_length=255, choices=[('Pending', 'Pending'), ('Delivered', 'Delivered')], default='Pending')


    def __str__(self):
        return self.user.username + ' - ' + self.delivery_status


class Food(models.Model):
    name = models.CharField(max_length=255)

class FoodDetails(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='food_details')
    name = models.CharField(max_length=255)
    stock_qty = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    photo_url = models.CharField(max_length=255, default=None)

    def __str__(self):
        return self.name
class OrderDetails(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='order_details')
    item = models.ForeignKey(FoodDetails, on_delete=models.CASCADE, related_name='order_details',default=1)
    qty = models.IntegerField()

class Payment(models.Model):
    order = models.OneToOneField(Orders, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=4, default=0.0000)
    created_at = models.DateTimeField(default=timezone.now,null=True, blank=True)
    razorpay_order_id=models.CharField(max_length=100,null=True, blank=True)
    razorpay_payment_id=models.CharField(max_length=100,null=True, blank=True)
    razorpay_signature=models.CharField(max_length=100,null=True, blank=True)

