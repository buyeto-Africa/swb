# apps/vendors/serializers.py
from rest_framework import serializers
from .models import VendorInvitation
from apps.userauths.models import User

# apps/vendors/serializers.py

from rest_framework import serializers
from .models import VendorProfile, VendorInvitation
from apps.userauths.models import User

class VendorInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorInvitation
        fields = ['email', 'business_name', 'token']
        read_only_fields = ['token']

class VendorProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = VendorProfile
        fields = [
            'id', 'email', 'phone', 'business_name', 'business_description',
            'business_address', 'business_phone', 'business_email',
            'registration_number', 'tax_id', 'logo', 'is_verified'
        ]

class VendorRegistrationSerializer(serializers.ModelSerializer):
    invitation_token = serializers.UUIDField(write_only=True)
    password = serializers.CharField(write_only=True)
    business_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone', 'password', 'invitation_token', 'business_name']

    def validate(self, data):
        try:
            invitation = VendorInvitation.objects.get(
                token=data['invitation_token'],
                email=data['email'],
                
            )

            # check if invitation is expired
            if invitation.is_expired:
                raise serializers.ValidationError({
                    "invitation": "Invitation link has expired"
                })
            # check if invitation is already used
            if invitation.is_accepted:
                raise serializers.ValidationError({
                    "invitation": "This invitation has already been used"
                })
            # Check if invitation is still valid
            if not invitation.can_be_used:
                raise serializers.ValidationError({
                    "invitation": "This invitation is no longer valid"
            })
            
            return data
        
        except VendorInvitation.DoesNotExist:
         raise serializers.ValidationError({
            "invitation": "Invalid invitation token"
         })

        



    def create(self, validated_data):
        invitation_token = validated_data.pop('invitation_token')
        validated_data['user_type'] = 'vendor'
        validated_data['is_email_verified'] = True
        user = User.objects.create_user(**validated_data)
        
        # Mark invitation as accepted
        invitation = VendorInvitation.objects.get(token=invitation_token)
        invitation.is_accepted = True
        invitation.save()
        
        return user