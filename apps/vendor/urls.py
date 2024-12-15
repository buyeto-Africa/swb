# apps/vendors/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    VendorProfileViewSet,
    VendorInvitationViewSet,
    
)

router = DefaultRouter()
router.register(r'profile', VendorProfileViewSet, basename='vendor-profile')
router.register(r'invitations', VendorInvitationViewSet, basename='vendor-invitations')


urlpatterns = [
    path('', include(router.urls)),
]