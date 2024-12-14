# apps/userauths/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate

from apps.vendor.models import VendorInvitation
from apps.staff.models import StaffInvitation
from apps.userauths.models import User




# apps/userauths/api/serializers.py

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
            if user.check_password(password):
                # Check email verification
                if not user.is_email_verified:
                    raise serializers.ValidationError(
                        'Email not verified',
                        code='email_not_verified'
                    )
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError(
                    'Invalid credentials',
                    code='invalid_credentials'
                )
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








    




class CustomerRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'phone', 'password']

    def create(self, validated_data):
        validated_data['user_type'] = 'customer'
        return User.objects.create_user(**validated_data)
    



class VendorRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    invitation_token = serializers.UUIDField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone', 'password', 'invitation_token']

    def validate(self, data):
        invitation = VendorInvitation.objects.filter(
            token=data['invitation_token'],
            email=data['email'],
            is_accepted=False
        ).first()
        if not invitation:
            raise serializers.ValidationError("Invalid invitation")
        return data

    def create(self, validated_data):
        invitation_token = validated_data.pop('invitation_token')
        validated_data['user_type'] = 'vendor'
        validated_data['is_email_verified'] = True
        user = User.objects.create_user(**validated_data)
        VendorInvitation.objects.filter(token=invitation_token).update(is_accepted=True)
        return user

class StaffRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    invitation_token = serializers.UUIDField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone', 'password', 'invitation_token']

    def validate(self, data):
        invitation = StaffInvitation.objects.filter(
            token=data['invitation_token'],
            email=data['email'],
            is_accepted=False
        ).first()
        if not invitation:
            raise serializers.ValidationError("Invalid invitation")
        return data

    def create(self, validated_data):
        invitation_token = validated_data.pop('invitation_token')
        validated_data['user_type'] = 'staff'
        validated_data['is_email_verified'] = True
        validated_data['is_staff'] = True
        user = User.objects.create_user(**validated_data)
        StaffInvitation.objects.filter(token=invitation_token).update(is_accepted=True)
        return user
    


