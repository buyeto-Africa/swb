from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.utils import timezone
import logging
import traceback

logger = logging.getLogger(__name__)

class EmailService:
    """Service class for handling email operations"""
    
    @staticmethod
    def send_invitation_email(invitation):
        """
        Send invitation email to the invited user
        
        Args:
            invitation: UserInvitation instance
            
        Returns:
            bool: True if email was sent successfully
        """
        try:
            # Log the start of email sending process
            logger.info("Starting email sending process...")
            
            context = {
                'user_type': invitation.get_user_type_display(),
                'invitation_link': EmailService._get_invitation_link(invitation),
                'expires_at': invitation.expires_at,
                'invited_by': invitation.invited_by.get_full_name() if invitation.invited_by else 'Administrator',
                'site_name': settings.SITE_NAME,
                'token': invitation.token,
            }
            
            # Log context for debugging
            logger.info(f"Email context prepared: {context}")
            
            try:
                # Render email templates
                logger.info("Rendering email templates...")
                html_content = render_to_string('accounts/emails/invitation.html', context)
                text_content = strip_tags(html_content)
                logger.info("Email templates rendered successfully")
            except Exception as template_error:
                logger.error(f"Template rendering error: {template_error}")
                logger.error(traceback.format_exc())
                return False
            
            # Create email
            subject = f'Invitation to join {settings.SITE_NAME} as {invitation.get_user_type_display()}'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = invitation.email
            
            logger.info(f"Email details:")
            logger.info(f"- To: {to_email}")
            logger.info(f"- From: {from_email}")
            logger.info(f"- Subject: {subject}")
            logger.info(f"- Backend: {settings.EMAIL_BACKEND}")
            
            try:
                # Create message and attach content
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
                msg.attach_alternative(html_content, "text/html")
                logger.info("Email message created successfully")
                
                # Get connection and send
                logger.info("Attempting to send email...")
                connection = get_connection(fail_silently=False)
                logger.info("Got email connection")
                
                # Print email content to console for debugging
                logger.info("Email Content:")
                logger.info("-------------")
                logger.info(f"Subject: {subject}")
                logger.info(f"From: {from_email}")
                logger.info(f"To: {to_email}")
                logger.info("Text Content:")
                logger.info(text_content)
                logger.info("HTML Content:")
                logger.info(html_content)
                logger.info("-------------")
                
                sent = msg.send()
                logger.info(f"Email sent successfully: {sent}")
                
                if sent:
                    invitation.email_sent = True
                    invitation.email_sent_at = timezone.now()
                    invitation.save(update_fields=['email_sent', 'email_sent_at'])
                    return True
                return False
                
            except Exception as send_error:
                logger.error(f"Error sending email: {send_error}")
                logger.error(traceback.format_exc())
                return False
            
        except Exception as e:
            logger.error(f"Unexpected error in send_invitation_email: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def _get_invitation_link(invitation):
        """Generate the invitation link with token"""
        invitation_path = reverse('accounts:invited-register')
        return f"{settings.SITE_URL}{invitation_path}?token={invitation.token}"
