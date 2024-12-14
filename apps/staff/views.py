# apps/staff/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import StaffRole, StaffProfile, StaffInvitation
from .serializers import (
    StaffRoleSerializer,
    StaffProfileSerializer,
    StaffInvitationSerializer,
    StaffRegistrationSerializer
)

class HasStaffPermission:
    """Custom permission to check if user has staff management permissions"""
    def has_permission(self, request, view):
        return (
            request.user.is_superuser or 
            (hasattr(request.user, 'staff_profile') and 
             request.user.staff_profile.role.permissions.get('manage_staff', False))
        )

class StaffRoleViewSet(viewsets.ModelViewSet):
    queryset = StaffRole.objects.all()
    serializer_class = StaffRoleSerializer
    permission_classes = [IsAuthenticated, HasStaffPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(is_active=True)
        return queryset.select_related('created_by')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class StaffProfileViewSet(viewsets.ModelViewSet):
    serializer_class = StaffProfileSerializer
    permission_classes = [IsAuthenticated, HasStaffPermission]

    def get_queryset(self):
        queryset = StaffProfile.objects.select_related('user', 'role')
        if not self.request.user.is_superuser:
            queryset = queryset.filter(is_active=True)
        return queryset

    @action(detail=True, methods=['post'])
    def change_role(self, request, pk=None):
        profile = self.get_object()
        try:
            new_role = StaffRole.objects.get(
                id=request.data.get('role_id'),
                is_active=True
            )
            profile.role = new_role
            profile.save()
            return Response({
                'message': 'Role updated successfully',
                'new_role': StaffRoleSerializer(new_role).data
            })
        except StaffRole.DoesNotExist:
            return Response(
                {'error': 'Invalid or inactive role ID'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        profile = self.get_object()
        profile.is_active = not profile.is_active
        profile.save()
        return Response({
            'message': f"Staff member {'activated' if profile.is_active else 'deactivated'}",
            'is_active': profile.is_active
        })

class StaffInvitationViewSet(viewsets.ModelViewSet):
    serializer_class = StaffInvitationSerializer
    permission_classes = [IsAuthenticated, HasStaffPermission]

    def get_queryset(self):
        return (StaffInvitation.objects
                .select_related('role', 'invited_by')
                .order_by('-created_at'))

    def _send_invitation_email(self, invitation, is_resend=False):
        """Helper method to send invitation emails"""
        invitation_url = f"{settings.FRONTEND_URL}/staff/register?token={invitation.token}"
        subject = 'Staff Invitation' + (' (Resent)' if is_resend else '')
        send_mail(
            subject,
            f'You have been invited to join as {invitation.role.name}. '
            f'Click here to register: {invitation_url}',
            settings.DEFAULT_FROM_EMAIL,
            [invitation.email],
            fail_silently=False,
        )

    def perform_create(self, serializer):
        invitation = serializer.save(
            invited_by=self.request.user,
            expires_at=timezone.now() + timezone.timedelta(days=7)
        )
        self._send_invitation_email(invitation)

    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        invitation = self.get_object()
        if invitation.is_expired:
            invitation.expires_at = timezone.now() + timezone.timedelta(days=7)
            invitation.save()
        
        self._send_invitation_email(invitation, is_resend=True)
        return Response({'message': 'Invitation resent successfully'})

class StaffRegistrationViewSet(viewsets.GenericViewSet):
    serializer_class = StaffRegistrationSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "Staff member registered successfully",
            "email": user.email,
            "role": user.staff_profile.role.name
        }, status=status.HTTP_201_CREATED)