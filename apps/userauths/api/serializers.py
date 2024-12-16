from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.staff.models import StaffInvitation
from apps.userauths.models import User
from apps.vendor.models import VendorInvitation, VendorProfile 
from django.db import transaction
from apps.customer.models import CustomerProfile

from apps.vendor.models import VendorProfile, VendorInvitation
from django.core.exceptions import ValidationError







class CustomerRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = User
        fields = ['email', 'phone', 'password', 'first_name', 'last_name']

    def validate_phone(self, value):
        """
        Validate phone number format
        """
        phone_validator = User._meta.get_field('phone').validators[0]
        try:
            phone_validator(value)
            return value
        except ValidationError:
            # Return the error directly without wrapping it in a dictionary
            raise serializers.ValidationError(
                "Phone number must be entered in the format: '+999999999'"
            )

    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        
        validated_data['user_type'] = 'customer'
        user = User.objects.create_user(**validated_data)

        # Update the customer profile
        user.customer_profile.first_name = first_name
        user.customer_profile.last_name = last_name
        user.customer_profile.save()

        return user




class VendorRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    invitation_token = serializers.UUIDField(write_only=True)
    business_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone', 'password', 'invitation_token', 'business_name']

    def validate(self, data):
        try:
            invitation = VendorInvitation.objects.get(
                token=data['invitation_token'],
                email=data['email']
            )
            
            if invitation.is_expired:
                raise serializers.ValidationError({
                    'non_field_errors':['Invitation has expired']})
                
            if invitation.is_accepted:
                raise serializers.ValidationError({
                    'non_field_errors':['Invitation has already been used']})
                
            self.context['invitation'] = invitation
            data['business_name'] = invitation.business_name
            return data
            
        except VendorInvitation.DoesNotExist:
            raise serializers.ValidationError({
                'non_field_errors':['Invalid invitation']})

    @transaction.atomic
    def create(self, validated_data):
        # Remove non-User model fields
        invitation_token = validated_data.pop('invitation_token')
        business_name = validated_data.pop('business_name')
        password = validated_data.pop('password')
        
        # Create the user
        user = User(**validated_data)
        user.set_password(password)
        user.user_type = 'vendor'
        user.is_email_verified = True
        user.save()

        # Create vendor profile
        

        VendorProfile.objects.create(
            user=user,
            business_name=business_name
                # business_email=user.email,
                # business_phone=user.phone
            )

        # Mark invitation as accepted
        invitation = self.context.get('invitation')
        
        invitation.is_accepted = True
        invitation.save()

        return user
    
    
    

        



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError(
                'Must include "email" and "password"',
                code='missing_fields'
            )

        try:
            user = User.objects.get(email=email)

            if not user.check_password(password):
                raise serializers.ValidationError(
                    'Invalid credentials',
                    code='invalid_credentials'
                )
            
            if not user.is_email_verified:
                raise serializers.ValidationError(
                    'Email not verified',
                    code='email_not_verified'
                )
            
            attrs['user'] = user
            return attrs 
        
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Invalid credentials',
                code='invalid_credentials'
            )

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'user_type', 'is_email_verified']
        read_only_fields = ['is_email_verified']

# class CustomerRegistrationSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
    
#     class Meta:
#         model = User
#         fields = ['email', 'phone', 'password']

#     def create(self, validated_data):
#         validated_data['user_type'] = 'customer'
#         return User.objects.create_user(**validated_data)



class StaffRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    invitation_token = serializers.UUIDField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone', 'password', 'invitation_token']

    def validate(self, data):
        try:
            invitation = StaffInvitation.objects.get(
                token=data['invitation_token'],
                email=data['email']
            )
            if invitation.is_expired:
                raise serializers.ValidationError("Invitation has expired")
            if invitation.is_accepted:
                raise serializers.ValidationError("Invitation has already been used")
            return data
        except StaffInvitation.DoesNotExist:
            raise serializers.ValidationError("Invalid invitation")

    def create(self, validated_data):
        invitation_token = validated_data.pop('invitation_token')
        validated_data['user_type'] = 'staff'
        validated_data['is_email_verified'] = True
        validated_data['is_staff'] = True
        user = User.objects.create_user(**validated_data)
        StaffInvitation.objects.filter(token=invitation_token).update(is_accepted=True)
        return user
