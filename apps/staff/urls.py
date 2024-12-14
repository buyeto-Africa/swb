# apps/staff/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import StaffRoleViewSet, StaffProfileViewSet, StaffInvitationViewSet

router = DefaultRouter()
router.register(r'roles', StaffRoleViewSet)
router.register(r'profiles', StaffProfileViewSet, basename='staff-profile')  # Add basename
router.register(r'invitations', StaffInvitationViewSet, basename='staff-invitations') 

urlpatterns = [
    path('', include(router.urls)),
]