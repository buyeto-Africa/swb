# apps/userauths/api/views.py

from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import UserRateThrottle

from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from apps.userauths.throttles import PasswordResetRateThrottle




from apps.userauths.models import User, PasswordReset
from .serializers import (
    LoginSerializer, 
    UserSerializer,
    VendorRegistrationSerializer,
    CustomerRegistrationSerializer
)
from .password_serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordChangeSerializer
)

class PasswordResetThrottle(UserRateThrottle):
    rate = '3/hour'

class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        serializer_map = {
            'login': LoginSerializer,
            'vendor_register': VendorRegistrationSerializer,
            'customer_register': CustomerRegistrationSerializer,
            'request_reset': PasswordResetRequestSerializer,
            'reset_password': PasswordResetConfirmSerializer,
            'change_password': PasswordChangeSerializer
        }
        return serializer_map.get(self.action, LoginSerializer)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            return Response(self._generate_tokens(user))
        except serializers.ValidationError as e:
            error_message = str(e.detail['non_field_errors'][0]) if 'non_field_errors' in e.detail else str(e.detail)
            return Response({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'])
    def vendor_register(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response({
                'message': 'Vendor registration successful',
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            error_message = str(e.detail['non_field_errors'][0]) if 'non_field_errors' in e.detail else str(e.detail)
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def customer_register(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response({
                'message': 'Registration successful. Please check your email for verification.',
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response({'error': str(e.detail)}, status=status.HTTP_400_BAD_REQUEST)
        



    

    # @action(detail=False, methods=['post'])
    # @throttle_classes([PasswordResetThrottle])
    # def request_reset(self, request):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     email = serializer.validated_data['email']

    #     try:
    #         user = User.objects.get(email=email)
    #         reset_token = PasswordReset.objects.create(
    #             user=user,
    #             expires_at=timezone.now() + timezone.timedelta(hours=1)
    #         )
    #         return Response({'message': 'Password reset instructions sent to your email'})
    #     except User.DoesNotExist:
    #         return Response({'error': 'No account found with this email'}, status=status.HTTP_400_BAD_REQUEST)


    # @action(detail=False, methods=['post'])
    # def request_reset(self, request):
    #     """Request password reset"""
    #     serializer = PasswordResetRequestSerializer(data=request.data)
    #     if serializer.is_valid():
    #         email = serializer.validated_data['email']
    #         try:
    #             user = User.objects.get(email=email)
    #             # Create password reset token
    #             reset_token = PasswordReset.objects.create(
    #                 user=user,
    #                 expires_at=timezone.now() + timezone.timedelta(hours=24)
    #             )
    #             # Here you would typically send an email with the reset token
    #             return Response({
    #                 'message': 'Password reset instructions sent to your email'
    #             })
    #         except User.DoesNotExist:
    #             # Return same message even if email doesn't exist for security
    #             return Response({
    #                 'message': 'Password reset instructions sent to your email'
    #             })
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    # @action(detail=False, methods=['post'], throttle_classes=[PasswordResetRateThrottle])
    # def request_reset(self, request):
    #     serializer = PasswordResetRequestSerializer(data=request.data)
    #     if serializer.is_valid():
    #         email = serializer.validated_data['email']
    #         try:
    #             user = User.objects.get(email=email)
    #             # Create password reset token
    #             reset_token = PasswordReset.objects.create(
    #                 user=user,
    #                 expires_at=timezone.now() + timezone.timedelta(hours=24)
    #             )
    #             return Response({
    #                 'message': 'Password reset instructions sent to your email'
    #             })
    #         except User.DoesNotExist:
    #             return Response({
    #                 'message': 'Password reset instructions sent to your email'
    #             })
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    





    @action(detail=False, methods=['post'])
    def request_reset(self, request):
        """Request password reset"""
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        # First validate the data
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        email = serializer.validated_data['email']
        
        # Apply throttling only for valid emails that exist in the system
        try:
            user = User.objects.get(email=email)
            
            # Check throttling
            throttle = PasswordResetRateThrottle()
            if not throttle.allow_request(request, self):
                return Response(
                    {"error": "Too many password reset attempts. Please try again later."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
                
            # Create password reset token
            reset_token = PasswordReset.objects.create(
                user=user,
                expires_at=timezone.now() + timezone.timedelta(hours=24)
            )
            
            # Here you would typically send an email with the reset token
            return Response({
                'message': 'Password reset instructions sent to your email'
            })
            
        except User.DoesNotExist:
            # Return same message even if email doesn't exist for security
            return Response({
                'message': 'Password reset instructions sent to your email'
            })




    @action(detail=False, methods=['post'], url_path='password/reset')
    def reset_password(self, request):
        """Reset password with token"""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            reset_request = serializer.validated_data['reset_request']
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            reset_request.used_at = timezone.now()
            reset_request.save()
            
            return Response({'message': 'Password reset successful'})
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # apps/userauths/api/views.py

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """Reset password with token"""
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            # Return the error message directly without wrapping it
            error_message = next(iter(serializer.errors.values()))[0]
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
    
        try:
            serializer.save()
            return Response({'message': 'Password reset successful'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _generate_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_type': user.user_type,
            'email': user.email
        }

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]