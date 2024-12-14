# apps/userauths/api/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import UserViewSet, AuthViewSet  # Remove LoginView from import

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    # Login endpoint
    path('login/', AuthViewSet.as_view({'post': 'login'}), name='login'),
    
    # Registration endpoints
    path('register/customer/', 
         AuthViewSet.as_view({'post': 'customer_register'}), 
         name='customer-register'),
    path('register/vendor/', 
         AuthViewSet.as_view({'post': 'vendor_register'}), 
         name='vendor-register'),
    path('register/staff/', 
         AuthViewSet.as_view({'post': 'staff_register'}), 
         name='staff-register'),
    
    # Email verification endpoints
    path('verify-email/', 
         AuthViewSet.as_view({'get': 'verify_email'}), 
         name='verify-email'),
    path('resend-verification/', 
         AuthViewSet.as_view({'post': 'resend_verification'}), 
         name='resend-verification'),
    
    # Include router URLs
    path('', include(router.urls)),
]