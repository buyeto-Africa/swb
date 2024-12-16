# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from apps.userauths.models import User

# class UserAuthenticationTests(APITestCase):
#     def setUp(self):
#         print("\nTest Setup State:")
#         # Create test users with proper password setting
#         self.admin = User.objects.create_user(
#             email='admin@example.com',
#             password='testpass123',
#             phone='+1234567890',
#             user_type='staff',
#             is_staff=True,
#             is_superuser=True
#         )
#         print("Admin user created: admin@example.com")

#         self.verified_user = User.objects.create_user(
#             email='verified@example.com',
#             password='testpass123',
#             phone='+1234567890',
#             user_type='customer',
#             is_email_verified=True
#         )
#         print("Verified user created: verified@example.com")

#         self.unverified_user = User.objects.create_user(
#             email='unverified@example.com',
#             password='testpass123',
#             phone='+1234567890',
#             user_type='customer',
#             is_email_verified=False
#         )
#         print("Unverified user created: unverified@example.com")

#         self.login_url = reverse('auth-login')

#     def test_customer_login_success(self):
#         data = {
#             'email': 'verified@example.com',
#             'password': 'testpass123'
#         }
        
#         print("\nVerified user state:")
#         print(f"Email: {self.verified_user.email}")
#         print(f"Is verified: {self.verified_user.is_email_verified}")
#         print(f"User type: {self.verified_user.user_type}")
        
#         response = self.client.post(self.login_url, data=data, format='json')
        
#         print("\nLogin Response:")
#         print(f"Status Code: {response.status_code}")
#         print(f"Content: {response.json()}")
        
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('access', response.data)
#         self.assertIn('refresh', response.data)

#     def test_customer_login_unverified_email(self):
#         data = {
#             'email': 'unverified@example.com',
#             'password': 'testpass123'
#         }
        
#         response = self.client.post(self.login_url, data=data, format='json')
        
#         print("\nUnverified Login Response:")
#         print(f"Status Code: {response.status_code}")
#         print(f"Content: {response.json()}")
        
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#         self.assertEqual(response.json()['error'], 'Email not verified')

#     def test_customer_login_wrong_password(self):
#         data = {
#             'email': 'verified@example.com',
#             'password': 'wrongpass123'
#         }
        
#         response = self.client.post(self.login_url, data=data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#         self.assertEqual(response.json()['error'], 'Invalid credentials')

#     def test_customer_login_nonexistent_user(self):
#         data = {
#             'email': 'nonexistent@example.com',
#             'password': 'testpass123'
#         }
        
#         response = self.client.post(self.login_url, data=data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#         self.assertEqual(response.json()['error'], 'Invalid credentials')

#     def tearDown(self):
#         User.objects.all().delete()
#         print("\nTest Cleanup: All users deleted")







# apps/userauths/tests/test_auth.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from apps.userauths.models import User
from apps.vendor.models import VendorInvitation
import uuid

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.vendor_register_url = reverse('auth-vendor-register')
        self.customer_register_url = reverse('auth-customer-register')
        self.login_url = reverse('auth-login')
        """Set up test data"""
        # Create test users
        self.customer = User.objects.create_user(
            email='customer@example.com',
            phone='+1234567890',
            password='testpass123',
            user_type='customer',
            is_email_verified=True
        )
        
        self.vendor = User.objects.create_user(
            email='vendor@example.com',
            phone='+1234567891',
            password='testpass123',
            user_type='vendor',
            is_email_verified=True
        )

        self.unverified_user = User.objects.create_user(
            email='unverified@example.com',
            phone='+1234567892',
            password='testpass123',
            is_email_verified=False
        )

        # Create URLs
        self.login_url = reverse('auth-login')
        self.customer_register_url = reverse('auth-customer-register')
        self.vendor_register_url = reverse('auth-vendor-register')

    def test_login_success(self):
        """Test successful login"""
        data = {
            'email': 'customer@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user_type'], 'customer')

    def test_login_unverified_email(self):
        """Test login with unverified email"""
        data = {
            'email': 'unverified@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], 'Email not verified')

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'email': 'customer@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], 'Invalid credentials')

class CustomerRegistrationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('auth-customer-register')
        self.valid_data = {
            'email': 'newcustomer@example.com',
            'phone': '+1234567890',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'Customer'
        }

    def test_customer_registration_success(self):
        """Test successful customer registration"""
        response = self.client.post(self.register_url, self.valid_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['message'], 
            'Registration successful. Please check your email for verification.'
        )
        
        # Verify user was created
        user = User.objects.get(email='newcustomer@example.com')
        self.assertEqual(user.user_type, 'customer')
        self.assertFalse(user.is_email_verified)

    # apps/userauths/tests/test_auth.py

    def test_customer_registration_duplicate_email(self):
        """Test registration with existing email"""
        # First registration
        self.client.post(self.register_url, self.valid_data)
        
        # Second registration with same email
        response = self.client.post(self.register_url, self.valid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('email', str(response.data['error']))  # Check if 'email' is in the error message

class VendorRegistrationTests(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            phone='+1234567890',
            password='adminpass123'
        )

        # Create vendor invitation
        self.invitation = VendorInvitation.objects.create(
            email='newvendor@example.com',
            business_name='Test Vendor',
            invited_by=self.admin,
            expires_at=timezone.now() + timezone.timedelta(days=7)
        )

        self.register_url = reverse('auth-vendor-register')
        self.valid_data = {
            'email': 'newvendor@example.com',
            'phone': '+1234567891',
            'password': 'testpass123',
            'invitation_token': str(self.invitation.token),
            'business_name': 'Test Vendor'
        }

    def test_vendor_registration_success(self):
        """Test successful vendor registration"""
        response = self.client.post(self.register_url, self.valid_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Vendor registration successful')
        
        # Verify user was created
        user = User.objects.get(email='newvendor@example.com')
        self.assertEqual(user.user_type, 'vendor')
        self.assertTrue(user.is_email_verified)

    def test_vendor_registration_invalid_token(self):
        """Test registration with invalid invitation token"""
        invalid_data = self.valid_data.copy()
        invalid_data['invitation_token'] = str(uuid.uuid4())
        
        response = self.client.post(self.register_url, invalid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_vendor_registration_expired_token(self):
        """Test registration with expired invitation"""
        # Set invitation to expired
        self.invitation.expires_at = timezone.now() - timezone.timedelta(days=1)
        self.invitation.save()
        
        response = self.client.post(self.register_url, self.valid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invitation has expired')

    def tearDown(self):
        """Clean up after tests"""
        User.objects.all().delete()
        VendorInvitation.objects.all().delete()