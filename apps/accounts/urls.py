from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views
from .views.auth import LoginView, LogoutView

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Registration URLs
    path('register/customer/', views.CustomerRegistrationView.as_view(), name='customer-register'),
    path('register/invited/', views.InvitedUserRegistrationView.as_view(), name='invited-register'),
]
