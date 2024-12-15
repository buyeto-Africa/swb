from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from apps.userauths.models import User
from .models import VendorProfile, VendorInvitation
from .serializers import (
    VendorProfileSerializer,
    VendorInvitationSerializer
    
)

class VendorInvitationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing vendor invitations.
    Only admin users can create and manage invitations.
    """
    queryset = VendorInvitation.objects.all()
    serializer_class = VendorInvitationSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        expires_at = timezone.now() + timezone.timedelta(days=7)
        serializer.save(
            invited_by=self.request.user,
            expires_at=expires_at
        )

    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        """Resend invitation email"""
        invitation = self.get_object()
        if invitation.is_accepted:
            return Response(
                {"error": "Invitation already accepted"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset expiration and resend email
        invitation.expires_at = timezone.now() + timezone.timedelta(days=7)
        invitation.save()
        
        # TODO: Add email sending logic here
        
        return Response({"message": "Invitation resent successfully"})

class VendorProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing vendor profiles.
    Vendors can only access their own profile, while staff can access all.
    """
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return VendorProfile.objects.all()
        return VendorProfile.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Allow staff to verify a vendor"""
        if not request.user.is_staff:
            return Response(
                {"error": "Not authorized"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        vendor_profile = self.get_object()
        vendor_profile.is_verified = True
        vendor_profile.save()
        
        return Response({"message": "Vendor verified successfully"})

# class VendorRegistrationViewSet(viewsets.GenericViewSet):
#     """
#     ViewSet for handling vendor registration.
#     Allows new vendors to register using their invitation.
#     """
#     serializer_class = VendorRegistrationSerializer
#     permission_classes = [AllowAny]

#     def create(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         # Create vendor user
#         validated_data = serializer.validated_data
#         invitation_token = validated_data.pop('invitation_token')
#         business_name = validated_data.pop('business_name')
        
#         try:
#             # Verify invitation is still valid
#             invitation = VendorInvitation.objects.get(
#                 token=invitation_token,
#                 email=validated_data['email'],
#                 is_accepted=False
#             )
#             if invitation.is_expired:
#                 return Response(
#                     {"error": "Invitation has expired"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # Create user and profile
#             validated_data['user_type'] = 'vendor'
#             validated_data['is_email_verified'] = True
#             user = User.objects.create_user(**validated_data)

#             # Update vendor profile
#             vendor_profile = user.vendor_profile
#             vendor_profile.business_name = business_name
#             vendor_profile.business_email = user.email
#             vendor_profile.business_phone = user.phone
#             vendor_profile.save()

#             # Mark invitation as accepted
#             invitation.is_accepted = True
#             invitation.save()

#             return Response(
#                 {
#                     "message": "Vendor registered successfully",
#                     "vendor_id": vendor_profile.id
#                 },
#                 status=status.HTTP_201_CREATED
#             )

#         except VendorInvitation.DoesNotExist:
#             return Response(
#                 {"error": "Invalid invitation"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         except Exception as e:
#             return Response(
#                 {"error": str(e)},
#                 status=status.HTTP_400_BAD_REQUEST
#             )