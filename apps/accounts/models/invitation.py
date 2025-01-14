from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid

from .user import User


def validate_non_customer(value):
    if value == User.UserType.CUSTOMER:
        raise ValidationError(_('Customers do not need invitations to register.'))


class UserInvitation(models.Model):
    """
    Model to handle invitations for non-customer users.
    Only platform staff can create invitations.
    """
    email = models.EmailField(_('email address'))
    user_type = models.CharField(
        _('user type'),
        max_length=50,
        choices=User.UserType.choices,
        validators=[validate_non_customer]
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='invitations_sent'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('user invitation')
        verbose_name_plural = _('user invitations')
        unique_together = ['email', 'user_type', 'is_used']  # Prevent duplicate active invitations

    def __str__(self):
        return f"Invitation for {self.email} as {self.user_type}"

    def save(self, *args, **kwargs):
        # Set expiration to 48 hours from creation if not set
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=48)
        super().save(*args, **kwargs)

    def send_invitation_email(self):
        """Send invitation email to the user"""
        from ..services.email_service import EmailService
        
        if not self.email_sent and not self.is_used and not self.is_expired:
            if EmailService.send_invitation_email(self):
                self.email_sent = True
                self.email_sent_at = timezone.now()
                self.save(update_fields=['email_sent', 'email_sent_at'])
                return True
        return False

    @property
    def is_expired(self):
        """Check if the invitation has expired"""
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        """Check if the invitation is still valid"""
        return not self.is_used and not self.is_expired
