from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, RefreshToken
from django.utils.translation import gettext_lazy as _

from ..models import User


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        
        # Add custom claims
        data['user_type'] = user.user_type
        data['email'] = user.email
        data['is_verified'] = user.is_verified
        data['is_approved'] = user.is_approved
        
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate_refresh(self, value):
        if not value:
            raise serializers.ValidationError(_('Refresh token is required'))
        return value
