from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _

from ..models import User, UserInvitation
from ..serializers import CustomerRegistrationSerializer, InvitedUserRegistrationSerializer


class CustomerRegistrationView(generics.CreateAPIView):
    """
    View for customer registration.
    This is the only registration endpoint that doesn't require an invitation.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomerRegistrationSerializer


class InvitedUserRegistrationView(generics.CreateAPIView):
    """
    View for invited user registration.
    Requires a valid invitation token.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = InvitedUserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        invitation_token = request.data.get('invitation_token')
        
        try:
            invitation = UserInvitation.objects.get(token=invitation_token)
            
            if not invitation.is_valid:
                if invitation.is_expired:
                    return Response(
                        {'error': _('Invitation has expired.')},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if invitation.is_used:
                    return Response(
                        {'error': _('Invitation has already been used.')},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Set the email from invitation
            request.data['email'] = invitation.email
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Create user with correct type
            user = serializer.save(
                user_type=invitation.user_type,
                is_approved=False  # All invited users need approval except customers
            )
            
            # Mark invitation as used
            invitation.is_used = True
            invitation.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except UserInvitation.DoesNotExist:
            return Response(
                {'error': _('Invalid invitation token.')},
                status=status.HTTP_400_BAD_REQUEST
            )
