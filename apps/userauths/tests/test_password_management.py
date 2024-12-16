# apps/userauths/tests/test_password_management.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from apps.userauths.models import User, PasswordReset
import uuid

class PasswordManagementTests(APITestCase):
    # apps/userauths/tests/test_password_management.py

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            phone='+1234567890'
        )
        self.password_reset_request_url = reverse('auth-request-reset')
        self.password_reset_confirm_url = reverse('auth-reset-password')
        
        # Create a verified user
        self.verified_user = User.objects.create_user(
            email='verified@example.com',
            phone='+1234567890',
            password='oldpass123',
            is_email_verified=True
        )
        
        # Create a password reset token
        self.reset_token = PasswordReset.objects.create(
            user=self.verified_user,
            expires_at=timezone.now() + timezone.timedelta(hours=24)
        )

    def test_password_reset_request_success(self):
        """Test successful password reset request"""
        data = {
            'email': self.verified_user.email
        }
        
        response = self.client.post(self.password_reset_request_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['message'], 
            'Password reset instructions sent to your email'
        )

    def test_password_reset_request_invalid_email(self):
        """Test password reset request with invalid email"""
        data = {
            'email': 'nonexistent@example.com'
        }
    
        response = self.client.post(self.password_reset_request_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(
            response.data['email']['error'], 
            'No account found with this email'
        )

    def test_password_reset_confirm_success(self):
        """Test successful password reset confirmation"""
        # Create a password reset token first
        self.reset_token = PasswordReset.objects.create(
            user=self.verified_user,
            token=uuid.uuid4()  # Generate a UUID token
        )
    
        data = {
            'token': str(self.reset_token.token),
            'user': self.verified_user.id,  # Add user ID
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
    
        response = self.client.post(self.password_reset_confirm_url, data)
    
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password reset successful')
    
        # Verify the password was actually changed
        self.verified_user.refresh_from_db()
        self.assertTrue(self.verified_user.check_password('newpass123'))
        
        # Verify the reset token was marked as used
        self.reset_token.refresh_from_db()
        self.assertIsNotNone(self.reset_token.used_at)

    def test_password_reset_confirm_invalid_token(self):
        """Test password reset confirmation with invalid token"""
        data = {
            'token': str(uuid.uuid4()),  # Random invalid token
            'email': self.verified_user.email,
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        
        response = self.client.post(self.password_reset_confirm_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid', str(response.data))

    def test_password_reset_confirm_passwords_mismatch(self):
        """Test password reset confirmation with mismatched passwords"""
        data = {
            'token': str(self.reset_token.token),
            'email': self.verified_user.email,
            'new_password': 'newpass123',
            'confirm_password': 'differentpass123'
        }
        
        response = self.client.post(self.password_reset_confirm_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Passwords don\'t match', str(response.data))

    def test_password_reset_confirm_expired_token(self):
        """Test password reset confirmation with expired token"""
        # Create expired reset token
        expired_token = PasswordReset.objects.create(
            user=self.verified_user,
            expires_at=timezone.now() - timezone.timedelta(hours=1)  # Expired
        )
        
        data = {
            'token': str(expired_token.token),
            'email': self.verified_user.email,
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        
        response = self.client.post(self.password_reset_confirm_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('expired', str(response.data).lower())