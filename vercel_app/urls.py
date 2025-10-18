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
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("Django is working! 🎉")





urlpatterns = [
    path('health/', health_check, name="health_check"),
    path('',index,name="index"),
    
    path('admin/', admin.site.urls),
    path('canteen/', include('canteen.urls',namespace='canteen')),
    path('admin_panel/', include('admin_panel.urls',namespace='admin_panel')),
    
    path('', include('database.urls')),
]

# add at the last
# urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

