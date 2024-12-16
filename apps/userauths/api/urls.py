# # apps/userauths/api/urls.py

# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import AuthViewSet, UserViewSet, PasswordManagementViewSet

# router = DefaultRouter()
# router.register(r'', AuthViewSet, basename='auth')
# router.register(r'users', UserViewSet, basename='user')
# router.register(r'password', PasswordManagementViewSet, basename='password')

# urlpatterns = [
#     # Explicit URL patterns for auth endpoints
#     path('login/', 
#          AuthViewSet.as_view({'post': 'login'}), 
#          name='auth-login'),
    
#     path('customer/register/', 
#          AuthViewSet.as_view({'post': 'customer_register'}), 
#          name='auth-customer-register'),
    
#     path('vendor/register/', 
#          AuthViewSet.as_view({'post': 'vendor_register'}), 
#          name='auth-vendor-register'),
    
#     path('password/reset/', 
#          AuthViewSet.as_view({'post': 'request_reset'}), 
#          name='auth-reset-password'),
    
#     path('password/reset/confirm/', 
#          AuthViewSet.as_view({'post': 'reset_password'}), 
#          name='auth-reset-password-confirm'),
    
#     path('password/change/', 
#          AuthViewSet.as_view({'post': 'change_password'}), 
#          name='auth-change-password'),
    
#     path('email/verify/', 
#          AuthViewSet.as_view({'get': 'verify_email'}), 
#          name='auth-verify-email'),

#     # Include router URLs
#     path('', include(router.urls)),
# ]


# apps/userauths/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserViewSet

router = DefaultRouter()
router.register(r'', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('login/', 
         AuthViewSet.as_view({'post': 'login'}), 
         name='auth-login'),
    
    path('vendor/register/', 
         AuthViewSet.as_view({'post': 'vendor_register'}), 
         name='auth-vendor-register'),
    
    path('customer/register/', 
         AuthViewSet.as_view({'post': 'customer_register'}), 
         name='auth-customer-register'),
    
    path('password/reset/', 
         AuthViewSet.as_view({'post': 'request_reset'}), 
         name='auth-reset-password'),
    
    path('password/reset/confirm/', 
         AuthViewSet.as_view({'post': 'reset_password'}), 
         name='auth-reset-password-confirm'),
    
    path('email/verify/', 
         AuthViewSet.as_view({'get': 'verify_email'}), 
         name='auth-verify-email'),


    path('password/reset/', 
        AuthViewSet.as_view({'post': 'request_password_reset'}), 
        name='auth-request-password-reset'),

    # Include router URLs
    path('', include(router.urls)),
]