# apps/customers/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CustomerProfileViewSet

router = DefaultRouter()
router.register(r'profile', CustomerProfileViewSet, basename='customer-profile')

urlpatterns = [
    path('', include(router.urls)),
]