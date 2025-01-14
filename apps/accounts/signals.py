from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserInvitation
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Create auth token for new users"""
    # TODO: Implement token creation if needed
    pass

@receiver(post_save, sender=UserInvitation)
def send_invitation_email(sender, instance, created, **kwargs):
    """Send invitation email when a new invitation is created"""
    logger.info(f"Signal received for invitation: {instance.email}")
    if created:
        logger.info(f"Sending invitation email to {instance.email}")
        success = instance.send_invitation_email()
        logger.info(f"Email sending {'successful' if success else 'failed'}")
