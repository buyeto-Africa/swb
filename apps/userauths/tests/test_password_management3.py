# apps/userauths/tests/test_password_management2.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from apps.userauths.models import User, PasswordReset
import uuid
from django.utils import timezone
from datetime import timedelta

class PasswordManagementTests(APITestCase):
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            phone='+1234567890',
            password='oldpassword123',
            is_email_verified=True
        )

        # Create password reset token
        self.reset_token = PasswordReset.objects.create(
            user=self.user,
            token=uuid.uuid4(),
            expires_at=timezone.now() + timedelta(hours=1)
        )

        # Set up URLs
        self.reset_request_url = reverse('auth-request-reset')
        self.reset_confirm_url = reverse('auth-reset-password')

    def test_password_reset_request_success(self):
        """Test successful password reset request"""
        data = {'email': 'test@example.com'}
        response = self.client.post(self.reset_request_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_password_reset_request_invalid_email(self):
        """Test password reset request with invalid email"""
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.reset_request_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_password_reset_confirm_success(self):
        """Test successful password reset confirmation"""
        data = {
            'token': str(self.reset_token.token),
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        response = self.client.post(self.reset_confirm_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_password_reset_confirm_invalid_token(self):
        """Test password reset confirmation with invalid token"""
        data = {
            'token': str(uuid.uuid4()),
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        response = self.client.post(self.reset_confirm_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_password_reset_confirm_passwords_mismatch(self):
        """Test password reset confirmation with mismatched passwords"""
        data = {
            'token': str(self.reset_token.token),
            'new_password': 'newpassword123',
            'confirm_password': 'differentpassword123'
        }
        response = self.client.post(self.reset_confirm_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def tearDown(self):
        """Clean up test data"""
        User.objects.all().delete()
        PasswordReset.objects.all().delete()