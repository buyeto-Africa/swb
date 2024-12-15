
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from apps.userauths.models import User
from .serializers import (
    LoginSerializer, 
    UserSerializer,
    VendorRegistrationSerializer,
    CustomerRegistrationSerializer,
)
from ..models import User







# apps/userauths/api/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import VendorRegistrationSerializer, LoginSerializer


# apps/userauths/api/views.py

# apps/userauths/api/views.py



# apps/userauths/api/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import LoginSerializer

class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user_type': user.user_type,
                'email': user.email
            })
        except serializers.ValidationError as e:
            if 'non_field_errors' in e.detail:
                error_message = str(e.detail['non_field_errors'][0])
            else:
                error_message = str(e.detail)

            return Response(
                {'error': error_message},
                status=status.HTTP_401_UNAUTHORIZED
            )



    @action(detail=False, methods=['post'])
    def vendor_register(self, request):
        serializer = VendorRegistrationSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response({
                'message': 'Vendor registration successful',
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            error_message = str(e.detail['non_field_errors'][0]) if 'non_field_errors' in e.detail else str(e.detail)
            return Response(
                    {'error': error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
            






    @action(detail=False, methods=['get'])
    def verify_email(self, request):
        """Verify user email with token"""
        token = request.query_params.get('token')
        if not token:
            return Response(
                {'error': 'Verification token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email_verification_token=token)
            if user.is_email_verified:
                return Response({'message': 'Email already verified'})

            user.is_email_verified = True
            user.email_verification_token = None
            user.save()

            return Response({'message': 'Email verified successfully'})
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid verification token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    

    
    def get_serializer_class(self):
        if self.action == 'login':
            return LoginSerializer
        elif self.action == 'vendor_register':
            return VendorRegistrationSerializer
        return LoginSerializer

    def _generate_tokens(self, user):
        """Helper method to generate JWT tokens"""
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
    def customer_register(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            return Response({
                "message": 'Registration successful. Please check your email for verification.',
                 'email': user.email
                 },status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response(
                {'error': str(e.detail)},
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





# apps/userauths/api/views.py

