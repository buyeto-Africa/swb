from django.shortcuts import render

# Create your views here.


# apps/vendors/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import VendorProfile, VendorInvitation
from .serializers import (
    VendorProfileSerializer,
    VendorInvitationSerializer,
    VendorRegistrationSerializer
)




class VendorInvitationViewSet(viewsets.ModelViewSet):
    queryset = VendorInvitation.objects.all()
    serializer_class = VendorInvitationSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        # Set expiration to 7 days from now
        expires_at = timezone.now() + timezone.timedelta(days=7)
        serializer.save(
            invited_by=self.request.user,
            expires_at=expires_at
        )

class VendorProfileViewSet(viewsets.ModelViewSet):
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return VendorProfile.objects.all()
        return VendorProfile.objects.filter(user=self.request.user)

class VendorRegistrationViewSet(viewsets.GenericViewSet):
    serializer_class = VendorRegistrationSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create vendor user
        validated_data = serializer.validated_data
        invitation_token = validated_data.pop('invitation_token')
        business_name = validated_data.pop('business_name')
        
        validated_data['user_type'] = 'vendor'
        validated_data['is_email_verified'] = True
        user = User.objects.create_user(**validated_data)

        # Update vendor profile
        vendor_profile = user.vendor_profile
        vendor_profile.business_name = business_name
        vendor_profile.save()

        # Mark invitation as accepted
        VendorInvitation.objects.filter(token=invitation_token).update(is_accepted=True)

        return Response(
            {"message": "Vendor registered successfully"},
            status=status.HTTP_201_CREATED
        )