from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User, UserInvitation


class InvitedUserRegistrationForm(UserCreationForm):
    """Form for invited users to complete their registration"""
    invitation_token = forms.UUIDField(widget=forms.HiddenInput())
    company_name = forms.CharField(
        max_length=255,
        required=True,
        help_text=_('Your company or organization name')
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        help_text=_('Your contact phone number')
    )
    
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'company_name',
            'phone_number',
            'password1',
            'password2',
        )
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make names required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        
    def clean_invitation_token(self):
        token = self.cleaned_data.get('invitation_token')
        try:
            invitation = UserInvitation.objects.get(token=token)
            if invitation.is_expired:
                raise ValidationError(_('This invitation has expired. Please request a new one.'))
            if invitation.is_used:
                raise ValidationError(_('This invitation has already been used.'))
            return token
        except UserInvitation.DoesNotExist:
            raise ValidationError(_('Invalid invitation token.'))
