from django.contrib import admin

# Register your models here.
from .models import CustomUser, Orders, OrderDetails, Payment, Food, FoodDetails

admin.site.register(CustomUser)
admin.site.register(Orders)
admin.site.register(OrderDetails)
admin.site.register(Payment)
admin.site.register(Food)
admin.site.register(FoodDetails)
