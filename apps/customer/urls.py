# apps/customers/urls.py

# from rest_framework.routers import DefaultRouter
# from django.urls import path, include
# from .views import CustomerProfileViewSet

# router = DefaultRouter()
# router.register(r'profile', CustomerProfileViewSet, basename='customer-profile')

# urlpatterns = [
#     path('', include(router.urls)),
# ]




# apps/customers/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profile', views.CustomerProfileViewSet, basename='customer-profile')
router.register(r'addresses', views.CustomerAddressViewSet, basename='customer-address')
router.register(r'preferences', views.CustomerPreferencesViewSet, basename='customer-preferences')
router.register(r'orders', views.CustomerOrderViewSet, basename='customer-orders')
router.register(r'wishlist', views.CustomerWishlistViewSet, basename='customer-wishlist')
router.register(r'reviews', views.CustomerReviewViewSet, basename='customer-reviews')

urlpatterns = [
    path('', include(router.urls)),
]