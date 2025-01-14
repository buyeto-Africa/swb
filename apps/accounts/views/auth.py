from django.utils.translation import gettext_lazy as _
from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import User
from ..serializers.auth import LoginSerializer, LogoutSerializer


class LoginView(TokenObtainPairView):
    """
    Login view that returns JWT tokens upon successful authentication
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]


class LogoutView(generics.GenericAPIView):
    """
    Logout view that blacklists the refresh token and handles different actor types
    """
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Get the refresh token
            refresh_token = serializer.validated_data['refresh']
            
            try:
                # Create token instance and blacklist it
                token = RefreshToken(refresh_token)
                token.blacklist()
                
                # Prepare response based on user type
                response_data = {
                    'detail': _('Successfully logged out'),
                    'user_type': request.user.user_type if request.user else None
                }
                
                return Response(response_data, status=status.HTTP_205_RESET_CONTENT)
                
            except Exception as token_error:
                return Response(
                    {'error': str(token_error)},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except serializers.ValidationError as e:
            return Response(
                {'error': str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': _('An error occurred during logout')}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
