# apps/customers/serializers.py

from rest_framework import serializers
from django.utils import timezone

from .models import CustomerProfile, CustomerOrder, CustomerAddress, CustomerWishlist  # Add CustomerOrder import
from apps.userauths.models import User







# apps/customer/serializers.py

from rest_framework import serializers
from .models import CustomerAddress

class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = [
            'id',
            'address_type',
            'street_address',
            'apartment',
            'city',
            'state',
            'country',
            'postal_code',
            'is_default',
            'phone_number'
        ]
        read_only_fields = ['id']

    def validate(self, data):
        # If this is the first address of this type, make it default
        request = self.context.get('request')
        if request and request.user:
            customer_profile = request.user.customer_profile
            existing_addresses = CustomerAddress.objects.filter(
                customer=customer_profile,
                address_type=data.get('address_type')
            )
            
            if not existing_addresses.exists():
                data['is_default'] = True
                
        return data

    def create(self, validated_data):
        if validated_data.get('is_default'):
            # Set all other addresses of same type to non-default
            CustomerAddress.objects.filter(
                customer=validated_data['customer'],
                address_type=validated_data['address_type']
            ).update(is_default=False)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('is_default'):
            # Set all other addresses of same type to non-default
            CustomerAddress.objects.filter(
                customer=instance.customer,
                address_type=validated_data.get('address_type', instance.address_type)
            ).exclude(id=instance.id).update(is_default=False)
        return super().update(instance, validated_data)


class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = [
            'id', 'address_type', 'street_address', 'apartment',
            'city', 'state', 'country', 'postal_code', 'is_default'
        ]



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






# apps/customers/serializers.py

from rest_framework import serializers
from .models import CustomerProfile, CustomerAddress, CustomerPreferences

class CustomerProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = [
            'id', 'email', 'phone', 'first_name', 'last_name', 
            'full_name', 'date_of_birth', 'profile_picture'
        ]





class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = [
            'id', 'address_type', 'street_address', 'city', 
            'state', 'country', 'postal_code', 'is_default'
        ]




# apps/customer/serializers.py

from rest_framework import serializers
from .models import CustomerPreferences

class CustomerPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerPreferences
        fields = [
            'id',
            'notification_preferences',
            'language_preference', 
            'currency_preference'
        ]




# apps/customer/serializers.py

from rest_framework import serializers
from apps.order.models import Order  # Make sure to import your Order model

class CustomerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'status',
            'total_amount',
            'created_at',
            'updated_at',
            # Add other relevant fields
        ]
        read_only_fields = ['order_number', 'status', 'total_amount']





# apps/customer/serializers.py

from rest_framework import serializers
from .models import CustomerWishlist

class CustomerWishlistSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    
    class Meta:
        model = CustomerWishlist
        fields = [
            'id',
            'product',
            'product_name',
            'product_price',
            'product_image',
            'added_at'
        ]
        read_only_fields = ['added_at']


# apps/customer/serializers.py

from rest_framework import serializers
from .models import CustomerReview

class CustomerReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = CustomerReview
        fields = [
            'id',
            'customer',
            'customer_name',
            'product',
            'product_name',
            'rating',
            'review_text',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['customer', 'created_at', 'updated_at']