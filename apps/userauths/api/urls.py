# apps/userauths/api/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import AuthViewSet

router = DefaultRouter()
router.register('auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
]