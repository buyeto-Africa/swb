# apps/userauths/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Invitation

class CustomerRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'customer'
        if commit:
            user.save()
        return user

class InvitedUserRegistrationForm(UserCreationForm):
    invitation_token = forms.UUIDField()

    class Meta:
        model = User
        fields = ['email', 'phone', 'password1', 'password2']

    def clean_invitation_token(self):
        token = self.cleaned_data.get('invitation_token')
        try:
            invitation = Invitation.objects.get(
                token=token,
                is_accepted=False,
                email=self.cleaned_data.get('email')
            )
            if invitation.is_expired:
                raise forms.ValidationError("This invitation has expired.")
        except Invitation.DoesNotExist:
            raise forms.ValidationError("Invalid invitation token.")
        return token

    def save(self, commit=True):
        user = super().save(commit=False)
        invitation = Invitation.objects.get(token=self.cleaned_data['invitation_token'])
        user.user_type = invitation.invitation_type
        user.is_email_verified = True
        if commit:
            user.save()
            invitation.is_accepted = True
            invitation.save()
        return user