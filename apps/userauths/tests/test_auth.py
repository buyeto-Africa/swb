from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.userauths.models import User

class UserAuthenticationTests(APITestCase):
    def setUp(self):
        print("\nTest Setup State:")
        # Create test users with proper password setting
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            phone='+1234567890',
            user_type='staff',
            is_staff=True,
            is_superuser=True
        )
        print("Admin user created: admin@example.com")

        self.verified_user = User.objects.create_user(
            email='verified@example.com',
            password='testpass123',
            phone='+1234567890',
            user_type='customer',
            is_email_verified=True
        )
        print("Verified user created: verified@example.com")

        self.unverified_user = User.objects.create_user(
            email='unverified@example.com',
            password='testpass123',
            phone='+1234567890',
            user_type='customer',
            is_email_verified=False
        )
        print("Unverified user created: unverified@example.com")

        self.login_url = reverse('auth-login')

    def test_customer_login_success(self):
        data = {
            'email': 'verified@example.com',
            'password': 'testpass123'
        }
        
        print("\nVerified user state:")
        print(f"Email: {self.verified_user.email}")
        print(f"Is verified: {self.verified_user.is_email_verified}")
        print(f"User type: {self.verified_user.user_type}")
        
        response = self.client.post(self.login_url, data=data, format='json')
        
        print("\nLogin Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Content: {response.json()}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_customer_login_unverified_email(self):
        data = {
            'email': 'unverified@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data=data, format='json')
        
        print("\nUnverified Login Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Content: {response.json()}")
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['error'], 'Email not verified')

    def test_customer_login_wrong_password(self):
        data = {
            'email': 'verified@example.com',
            'password': 'wrongpass123'
        }
        
        response = self.client.post(self.login_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['error'], 'Invalid credentials')

    def test_customer_login_nonexistent_user(self):
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['error'], 'Invalid credentials')

    def tearDown(self):
        User.objects.all().delete()
        print("\nTest Cleanup: All users deleted")
