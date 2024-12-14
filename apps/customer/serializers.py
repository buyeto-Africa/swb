# apps/customers/serializers.py

from rest_framework import serializers
from .models import CustomerProfile
from apps.userauths.models import User

class CustomerProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = CustomerProfile
        fields = [
            'id', 'email', 'phone', 'first_name', 'last_name', 
            'gender', 'date_of_birth', 'profile_picture',
            'address', 'city', 'state', 'country'
        ]

class CustomerEmailVerificationSerializer(serializers.Serializer):
    token = serializers.UUIDField()

    def validate_token(self, value):
        try:
            user = User.objects.get(
                email_verification_token=value,
                is_email_verified=False,
                user_type='customer'
            )
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid verification token")