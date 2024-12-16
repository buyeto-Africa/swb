from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.core.constants import SUPPORTED_CURRENCIES
from apps.core.services.currency import CurrencyConverter
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import (
    CustomerAddress, CustomerPreferences,
    CustomerOrder, CustomerWishlist, 
    CustomerReview
    )
from apps.order.models import Order



from .serializers import (
    CustomerProfileSerializer,
    CustomerEmailVerificationSerializer,
    CustomerAddressSerializer,
    CustomerPreferencesSerializer  # Add this import
)

# Create your views here.


# apps/customers/views.py
from apps.userauths.models import User
import uuid 
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomerProfile
from .serializers import CustomerProfileSerializer, CustomerEmailVerificationSerializer

class CustomerProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomerProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        serializer = CustomerEmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email_verification_token=serializer.validated_data['token'])
            user.is_email_verified = True
            user.email_verification_token = None
            user.save()
            return Response({"message": "Email verified successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def resend_verification(self, request):
        user = request.user
        if user.is_email_verified:
            return Response(
                {"message": "Email already verified"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.email_verification_token = uuid.uuid4()
        user.email_verification_sent_at = timezone.now()
        user.save()

        # Send verification email
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={user.email_verification_token}"
        send_mail(
            'Verify your email',
            f'Click the link to verify your email: {verification_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "Verification email sent"})
    




from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import CustomerProfile
from .serializers import CustomerProfileSerializer

class CustomerProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomerProfile.objects.filter(user=self.request.user)
    






# apps/customers/serializers.py


# apps/customers/views.py

class CustomerAddressViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomerAddress.objects.filter(customer__user=self.request.user)

    def perform_create(self, serializer):
        customer_profile = self.request.user.customer_profile
        if serializer.validated_data.get('is_default'):
            # Set all other addresses of same type to non-default
            CustomerAddress.objects.filter(
                customer=customer_profile,
                address_type=serializer.validated_data['address_type']
            ).update(is_default=False)
        serializer.save(customer=customer_profile)




    





class CustomerPreferencesViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerPreferencesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomerPreferences.objects.filter(customer__user=self.request.user)

    @action(detail=False, methods=['get'])
    def supported_currencies(self, request):
        return Response({
            'currencies': [
                {'code': code, 'name': name}
                for code, name in SUPPORTED_CURRENCIES
            ]
        })

    @action(detail=False, methods=['post'])
    def update_currency(self, request):
        currency = request.data.get('currency')
        if not currency:
            return Response(
                {'error': 'Currency is required'}, 
                status=400
            )

        valid_currencies = [code for code, _ in SUPPORTED_CURRENCIES]
        if currency not in valid_currencies:
            return Response(
                {'error': f'Invalid currency. Must be one of: {", ".join(valid_currencies)}'}, 
                status=400
            )

        preferences = self.get_queryset().first()
        preferences.currency_preference = currency
        preferences.save()

        return Response({
            'message': 'Currency preference updated successfully',
            'currency': currency
        })
    







# apps/customers/serializers.py



# apps/customers/views.py

# apps/customer/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    CustomerProfileSerializer,
    CustomerEmailVerificationSerializer,
    CustomerAddressSerializer,
    CustomerOrderSerializer  # Add this import
)

class CustomerOrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomerOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            customer=self.request.user.customer_profile
        )



# apps/customer/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import CustomerWishlist
from .serializers import (
    CustomerProfileSerializer,
    CustomerEmailVerificationSerializer,
    CustomerAddressSerializer,
    CustomerWishlistSerializer  # Add this import
)

class CustomerWishlistViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerWishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomerWishlist.objects.filter(
            customer=self.request.user.customer_profile
        )

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer_profile)


    




# apps/customer/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import CustomerReview
from .serializers import (
    CustomerProfileSerializer,
    CustomerEmailVerificationSerializer,
    CustomerAddressSerializer,
    CustomerOrderSerializer,
    CustomerReviewSerializer  # Add this import
)

class CustomerReviewViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomerReview.objects.filter(
            customer=self.request.user.customer_profile
        )

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer_profile)
