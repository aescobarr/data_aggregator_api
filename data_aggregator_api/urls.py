from django.contrib import admin
from django.urls import path
from django.conf.urls import include

from main.views import map_demo

urlpatterns = [
    path('', map_demo),
    path('admin/', admin.site.urls),
    path('api/', include('main.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
