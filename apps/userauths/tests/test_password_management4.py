# apps/userauths/tests/test_password_management4.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.core.cache import cache
from apps.userauths.models import User

class PasswordManagementTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            phone='+1234567890'
        )
        self.reset_url = reverse('auth-request-reset')
        cache.clear()  # Clear cache before testing

    def test_password_reset_rate_limiting(self):
        data = {'email': 'test@example.com'}
        
        # Make 3 requests (should be allowed)
        for _ in range(3):
            response = self.client.post(self.reset_url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Fourth request should be throttled
        response = self.client.post(self.reset_url, data)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)