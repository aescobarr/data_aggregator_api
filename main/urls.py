from django.conf.urls import url, include
from rest_framework import routers
from main import views

router = routers.DefaultRouter()
router.register(r'observation', views.ObservationViewSet)

urlpatterns = [
    url('', include(router.urls)),
]
