# apps/userauths/api/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
import uuid

from .serializers import (
    UserSerializer,
    LoginSerializer,
    CustomerRegistrationSerializer,
    VendorRegistrationSerializer,
    StaffRegistrationSerializer
)
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from apps.userauths.models import User









class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def get_serializer_class(self):
        actions = {
            'login': LoginSerializer,
            'customer_register': CustomerRegistrationSerializer,
            'vendor_register': VendorRegistrationSerializer,
            'staff_register': StaffRegistrationSerializer
        }
        return actions.get(self.action, self.serializer_class)

    def _generate_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_type': user.user_type,
            'email': user.email
        }
    



    def _authenticate_user(self, email, password):
        """Helper method to authenticate user"""
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                if not user.is_email_verified:
                    raise serializers.ValidationError(
                        'Email not verified',
                        code='email_not_verified'
                    )
                return user
        except User.DoesNotExist:
            pass
        
        raise serializers.ValidationError(
            'Invalid credentials',
            code='invalid_credentials'
        )

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            return Response(self._generate_tokens(user))
        except serializers.ValidationError as e:
            if 'non_field_errors' in e.detail:
                error = e.detail['non_field_errors'][0]
                if error.code == 'email_not_verified':
                    return Response(
                        {'error': 'Email not verified'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                elif error.code == 'invalid_credentials':
                    return Response(
                        {'error': 'Invalid credentials'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_400_BAD_REQUEST
            )
            

    @action(detail=False, methods=['post'])
    def customer_register(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response(
                {"message": "Registration successful"},
                status=status.HTTP_201_CREATED
            )
        except serializers.ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def vendor_register(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response(
                {"message": "Vendor registration successful"},
                status=status.HTTP_201_CREATED
            )
        except serializers.ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def staff_register(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response(
                {"message": "Staff registration successful"},
                status=status.HTTP_201_CREATED
            )
        except serializers.ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]