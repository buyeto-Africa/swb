# apps/customers/serializers.py

from rest_framework import serializers
from django.utils import timezone
from .models import CustomerProfile
from apps.userauths.models import User

class CustomerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for customer profile data with read-only user information
    """
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = [
            'id', 'email', 'phone', 'first_name', 'last_name', 
            'full_name', 'gender', 'date_of_birth', 'profile_picture',
            'address', 'city', 'state', 'country'
        ]

    def get_full_name(self, obj):
        """Returns the customer's full name or email username if name not set"""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.user.email.split('@')[0]

    def validate_date_of_birth(self, value):
        """Validate that date of birth is not in the future"""
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Date of birth cannot be in the future")
        return value

    def update(self, instance, validated_data):
        """
        Override update to handle nested updates and ensure certain fields
        remain read-only
        """
        for attr, value in validated_data.items():
            if attr not in ['email', 'phone']:  # Ensure these fields remain read-only
                setattr(instance, attr, value)
        instance.save()
        return instance

class CustomerEmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for handling customer email verification
    """
    token = serializers.UUIDField()

    def validate_token(self, value):
        """
        Validate the verification token and ensure it belongs to an unverified customer
        """
        try:
            user = User.objects.get(
                email_verification_token=value,
                is_email_verified=False,
                user_type='customer'
            )
            self.context['user'] = user  # Store user in context for later use
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired verification token")

    def save(self, **kwargs):
        """
        Complete the verification process
        """
        user = self.context.get('user')
        if user:
            user.is_email_verified = True
            user.email_verification_token = None  # Clear the token after use
            user.save()
            return user
        raise serializers.ValidationError("Unable to verify email")

class CustomerUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating customer profile with additional validation
    """
    class Meta:
        model = CustomerProfile
        fields = [
            'first_name', 'last_name', 'gender', 
            'date_of_birth', 'address', 'city', 
            'state', 'country'
        ]
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'gender': {'required': False},
            'date_of_birth': {'required': False},
            'address': {'required': False},
            'city': {'required': False},
            'state': {'required': False},
            'country': {'required': False}
        }