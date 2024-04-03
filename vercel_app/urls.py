"""vercel_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static



from canteen.views import index


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from database.views import CustomUserViewSet, OrdersViewSet, FoodViewSet, FoodDetailsViewSet, OrderDetailsViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'customusers', CustomUserViewSet)
router.register(r'orders', OrdersViewSet)
router.register(r'food', FoodViewSet)
router.register(r'fooddetails', FoodDetailsViewSet)
router.register(r'orderdetails', OrderDetailsViewSet)
router.register(r'payment', PaymentViewSet)


urlpatterns = [
    path('',index,name="index"),
    
    path('admin/', admin.site.urls),
    path('canteen/', include('canteen.urls',namespace='canteen')),
    path('admin_panel/', include('admin_panel.urls',namespace='admin_panel')),
    
    path('api/', include(router.urls)),
]

# add at the last
# urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

