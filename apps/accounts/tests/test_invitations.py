from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.core import mail
from datetime import timedelta
import uuid

from apps.accounts.models import User, UserInvitation
from apps.accounts.services.email_service import EmailService


class UserInvitationTests(TestCase):
    def setUp(self):
        # Create a staff user who can create invitations
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        
        # Create a basic invitation data
        self.invitation_data = {
            'email': 'test@example.com',
            'user_type': User.UserType.VENDOR,
            'invited_by': self.staff_user
        }

    def test_invitation_creation(self):
        """Test that invitations are created with correct data"""
        invitation = UserInvitation.objects.create(**self.invitation_data)
        
        self.assertEqual(invitation.email, self.invitation_data['email'])
        self.assertEqual(invitation.user_type, self.invitation_data['user_type'])
        self.assertEqual(invitation.invited_by, self.invitation_data['invited_by'])
        self.assertIsNotNone(invitation.token)
        self.assertFalse(invitation.is_used)
        self.assertIsNotNone(invitation.expires_at)

    def test_invitation_token_unique(self):
        """Test that each invitation gets a unique token"""
        invitation1 = UserInvitation.objects.create(**self.invitation_data)
        invitation2 = UserInvitation.objects.create(
            email='test2@example.com',
            user_type=User.UserType.VENDOR,
            invited_by=self.staff_user
        )
        
        self.assertNotEqual(invitation1.token, invitation2.token)

    def test_invitation_expiration(self):
        """Test invitation expiration logic"""
        invitation = UserInvitation.objects.create(**self.invitation_data)
        
        # Test valid invitation
        self.assertTrue(invitation.is_valid)
        
        # Test expired invitation
        invitation.expires_at = timezone.now() - timedelta(days=1)
        invitation.save(update_fields=['expires_at'])
        self.assertFalse(invitation.is_valid)

    def test_used_invitation(self):
        """Test that used invitations are marked correctly"""
        invitation = UserInvitation.objects.create(**self.invitation_data)
        
        self.assertFalse(invitation.is_used)
        invitation.is_used = True
        invitation.save(update_fields=['is_used'])
        
        # Refresh from database
        invitation.refresh_from_db()
        self.assertTrue(invitation.is_used)
        self.assertFalse(invitation.is_valid)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    SITE_URL='http://testserver'
)
class InvitationEmailTests(TestCase):
    def setUp(self):
        # Disable post_save signal temporarily
        from django.db.models.signals import post_save
        from apps.accounts.models.invitation import send_invitation_email
        post_save.disconnect(send_invitation_email, sender=UserInvitation)
        
        self.invitation = UserInvitation.objects.create(
            email='test@example.com',
            user_type=User.UserType.VENDOR
        )
        
        # Clear any emails that might have been sent during creation
        mail.outbox = []

    def test_invitation_email_sent(self):
        """Test that invitation emails are sent correctly"""
        # Send the invitation email
        EmailService.send_invitation_email(self.invitation)
        
        # Test that one message has been sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Verify the email content
        email = mail.outbox[0]
        self.assertEqual(email.to, [self.invitation.email])
        self.assertIn('Invitation to join', email.subject)
        self.assertIn(str(self.invitation.token), email.body)
        self.assertIn('Vendor', email.body)

    def test_email_tracking_fields(self):
        """Test that email sending updates tracking fields"""
        self.assertFalse(self.invitation.email_sent)
        self.assertIsNone(self.invitation.email_sent_at)
        
        EmailService.send_invitation_email(self.invitation)
        
        # Refresh from database
        self.invitation.refresh_from_db()
        self.assertTrue(self.invitation.email_sent)
        self.assertIsNotNone(self.invitation.email_sent_at)


class InvitationViewTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        
        # Disable post_save signal temporarily
        from django.db.models.signals import post_save
        from apps.accounts.models.invitation import send_invitation_email
        post_save.disconnect(send_invitation_email, sender=UserInvitation)
        
        self.invitation = UserInvitation.objects.create(
            email='test@example.com',
            user_type=User.UserType.VENDOR,
            invited_by=self.staff_user
        )
        self.register_url = reverse('accounts:invited-register')

    def test_register_with_valid_token(self):
        """Test registration with a valid invitation token"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '1234567890',
            'invitation_token': str(self.invitation.token)
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 201)
        
        # Verify user was created
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        user = User.objects.get(email='test@example.com')
        self.assertEqual(user.user_type, User.UserType.VENDOR)
        
        # Verify invitation was marked as used
        self.invitation.refresh_from_db()
        self.assertTrue(self.invitation.is_used)

    def test_register_with_invalid_token(self):
        """Test registration with invalid token"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '1234567890',
            'invitation_token': str(uuid.uuid4())
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 400)

    def test_register_with_expired_invitation(self):
        """Test registration with expired invitation"""
        self.invitation.expires_at = timezone.now() - timedelta(days=1)
        self.invitation.save(update_fields=['expires_at'])
        
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '1234567890',
            'invitation_token': str(self.invitation.token)
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 400)

    def test_register_with_used_invitation(self):
        """Test registration with already used invitation"""
        self.invitation.is_used = True
        self.invitation.save(update_fields=['is_used'])
        
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '1234567890',
            'invitation_token': str(self.invitation.token)
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 400)

    def test_global_buyer_invitation(self):
        """Test that Global Buyer invitations work correctly"""
        # Create a Global Buyer invitation
        invitation = UserInvitation.objects.create(
            email='global_buyer@example.com',
            user_type=User.UserType.GLOBAL_BUYER,
            invited_by=self.staff_user
        )

        # Send invitation email
        EmailService.send_invitation_email(invitation)

        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['global_buyer@example.com'])
        self.assertIn('Global Buyer', email.body)

        # Register with invitation
        data = {
            'email': 'global_buyer@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Global',
            'last_name': 'Buyer',
            'phone_number': '1234567890',
            'invitation_token': str(invitation.token)
        }
        response = self.client.post(reverse('accounts:invited-register'), data)
        self.assertEqual(response.status_code, 201)

        # Verify user was created with correct type
        user = User.objects.get(email='global_buyer@example.com')
        self.assertEqual(user.user_type, User.UserType.GLOBAL_BUYER)
        
        # Refresh invitation from database and verify it was marked as used
        invitation.refresh_from_db()
        self.assertTrue(invitation.is_used)
