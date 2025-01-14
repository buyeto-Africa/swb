from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from ..models import UserInvitation, GlobalBuyerProfile, VendorProfile, CustomerProfile

User = get_user_model()


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for customer registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    shipping_address = serializers.CharField(required=False)
    billing_address = serializers.CharField(required=False)
    newsletter_subscription = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = (
            'email', 'password', 'password_confirm', 'first_name', 'last_name', 
            'phone_number', 'shipping_address', 'billing_address', 'newsletter_subscription'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'phone_number': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': _("The two password fields didn't match.")})
        return attrs

    def create(self, validated_data):
        # Extract profile data
        profile_data = {
            'shipping_address': validated_data.pop('shipping_address', ''),
            'billing_address': validated_data.pop('billing_address', ''),
            'newsletter_subscription': validated_data.pop('newsletter_subscription', False)
        }
        
        # Remove password_confirm
        validated_data.pop('password_confirm')
        
        # Set user type and auto-approve
        validated_data['user_type'] = User.UserType.CUSTOMER
        validated_data['is_approved'] = True  # Customers are auto-approved
        
        # Create user
        user = User.objects.create_user(**validated_data)
        
        # Create customer profile
        CustomerProfile.objects.create(user=user, **profile_data)
        
        return user


class InvitedUserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for invited user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    invitation_token = serializers.UUIDField(write_only=True)
    
    # Global Buyer specific fields
    company_name = serializers.CharField(required=False, max_length=255)
    business_registration_number = serializers.CharField(required=False)
    tax_id = serializers.CharField(required=False)
    company_address = serializers.CharField(required=False)
    contact_person = serializers.CharField(required=False)

    # Vendor specific fields
    business_type = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'email', 'password', 'password_confirm', 'first_name', 'last_name', 
            'phone_number', 'invitation_token', 'company_name', 
            'business_registration_number', 'tax_id', 'company_address', 
            'contact_person', 'business_type'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'phone_number': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': _("The two password fields didn't match.")})
        
        # Validate invitation token
        try:
            invitation = UserInvitation.objects.get(
                token=attrs['invitation_token'],
                is_used=False
            )
            if not invitation.is_valid:
                raise serializers.ValidationError({'invitation_token': _("Invitation has expired or already been used.")})
            
            # For Global Buyers, validate required fields
            if invitation.user_type == User.UserType.GLOBAL_BUYER:
                required_fields = ['company_name', 'business_registration_number', 'tax_id', 
                                'company_address', 'contact_person']
                for field in required_fields:
                    if not attrs.get(field):
                        raise serializers.ValidationError({field: _("This field is required for Global Buyers.")})
            
            self.context['invitation'] = invitation
        except UserInvitation.DoesNotExist:
            raise serializers.ValidationError({'invitation_token': _("Invalid invitation token.")})
            
        return attrs

    def create(self, validated_data):
        # Remove non-model fields
        validated_data.pop('password_confirm')
        invitation_token = validated_data.pop('invitation_token')
        invitation = self.context['invitation']
        
        # Extract profile data based on user type
        profile_data = {}
        if invitation.user_type == User.UserType.GLOBAL_BUYER:
            profile_fields = ['company_name', 'business_registration_number', 'tax_id', 
                            'company_address', 'contact_person']
            profile_data = {
                field: validated_data.pop(field)
                for field in profile_fields
                if field in validated_data
            }
        elif invitation.user_type == User.UserType.VENDOR:
            profile_fields = ['company_name', 'tax_id', 'company_address', 
                            'company_registration_number', 'business_type']
            profile_data = {
                'store_name': validated_data.pop('company_name', ''),
                'store_description': validated_data.pop('business_type', ''),
                'store_address': validated_data.pop('company_address', ''),
            }
            # Remove other vendor-specific fields that we don't need
            for field in profile_fields:
                validated_data.pop(field, None)
        
        # Create user
        validated_data['user_type'] = invitation.user_type
        validated_data['email'] = invitation.email
        validated_data['is_approved'] = False  # All invited users need approval
        user = User.objects.create_user(**validated_data)
        
        # Create profile if needed
        if invitation.user_type == User.UserType.GLOBAL_BUYER:
            GlobalBuyerProfile.objects.create(user=user, **profile_data)
        elif invitation.user_type == User.UserType.VENDOR:
            VendorProfile.objects.create(user=user, **profile_data)
        
        # Mark invitation as used
        invitation.is_used = True
        invitation.save()
        
        return user
