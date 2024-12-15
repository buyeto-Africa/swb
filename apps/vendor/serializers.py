# apps/vendor/serializers.py

from rest_framework import serializers
from .models import VendorProfile, VendorInvitation

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