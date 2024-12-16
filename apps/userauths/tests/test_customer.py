# # apps/userauths/tests/test_customer.py

# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from apps.userauths.models import User
# from apps.customer.models import CustomerProfile

# class CustomerRegistrationTests(APITestCase):
#     def setUp(self):
#         """Set up test data"""
#         self.customer_register_url = reverse('auth-customer-register')
#         self.valid_customer_data = {
#             'email': 'customer@example.com',
#             'phone': '+1234567890',
#             'password': 'testpass123',
#             'first_name': 'Test',
#             'last_name': 'Customer'
#         }

#     def test_customer_registration_success(self):
#         """Test successful customer registration"""
#         response = self.client.post(
#             self.customer_register_url, 
#             self.valid_customer_data, 
#             format='json'
#         )
        
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data['message'], 'Registration successful. Please check your email for verification.')
#         self.assertEqual(response.data['email'], 'customer@example.com')

#         # Verify user was created
#         user = User.objects.get(email='customer@example.com')
#         self.assertEqual(user.user_type, 'customer')
#         self.assertFalse(user.is_email_verified)

#         # Verify customer profile was created
#         profile = CustomerProfile.objects.get(user=user)
#         self.assertEqual(profile.first_name, 'Test')
#         self.assertEqual(profile.last_name, 'Customer')

#     def test_duplicate_email_registration(self):
#         """Test registration with existing email"""
#         # First create a user
#         User.objects.create_user(
#             email='customer@example.com',
#             phone='+9876543210',
#             password='existingpass123',
#             user_type='customer'
#         )

#         response = self.client.post(
#             self.customer_register_url,
#             self.valid_customer_data,
#             format='json'
#         )

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('email', response.data['error'])
#         self.assertIn('already exists', str(response.data['error']))

#     def test_invalid_phone_number(self):
#         """Test registration with invalid phone number"""
#         invalid_data = self.valid_customer_data.copy()
#         invalid_data['phone'] = '123'  # Invalid phone format

#         response = self.client.post(
#             self.customer_register_url,
#             invalid_data,
#             format='json'
#         )

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertIn('phone', str(response.data['error']))
#         self.assertIn('+999999999', str(response.data['error']))

#     def test_missing_required_fields(self):
#         """Test registration with missing required fields"""
#         invalid_data = {
#             'email': 'customer@example.com'
#             # Missing other required fields
#         }

#         response = self.client.post(
#             self.customer_register_url,
#             invalid_data,
#             format='json'
#         )

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('password', response.data['error'])
#         self.assertIn('phone', response.data['error'])
#         self.assertIn('first_name', response.data['error'])
#         self.assertIn('last_name', response.data['error'])


   
        




# apps/userauths/tests/test_customer.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from apps.userauths.models import User, PasswordReset
from apps.customer.models import CustomerProfile
import uuid

class CustomerAuthenticationTests(APITestCase):
    def setUp(self):
        """Set up test data"""
        # Create base users first
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            phone='+1234567890',
            password='adminpass123'
        )

        self.verified_customer = User.objects.create_user(
            email='verified@example.com',
            phone='+1234567891',
            password='testpass123',
            user_type='customer',
            is_email_verified=True
        )

        self.unverified_user = User.objects.create_user(
            email='unverified@example.com',
            phone='+1234567892',
            password='testpass123',
            user_type='customer',
            is_email_verified=False
        )

        # Set up URLs
        self.customer_register_url = reverse('auth-customer-register')
        self.password_reset_request_url = reverse('auth-request-reset')
        self.password_reset_confirm_url = reverse('auth-reset-password')
        self.login_url = reverse('auth-login')

        # Test data
        self.valid_customer_data = {
            'email': 'customer@example.com',  # Changed from newcustomer@example.com
            'phone': '+1234567893',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'Customer'
        }

    def tearDown(self):
        """Clean up after each test"""
        User.objects.all().delete()
        CustomerProfile.objects.all().delete()



    def test_customer_registration_success(self):
        """Test successful customer registration"""
        response = self.client.post(
            self.customer_register_url, 
            self.valid_customer_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Registration successful. Please check your email for verification.')
        self.assertEqual(response.data['email'], 'customer@example.com')

        # Verify user was created
        user = User.objects.get(email='customer@example.com')
        self.assertEqual(user.user_type, 'customer')
        self.assertFalse(user.is_email_verified)

        # Verify customer profile was created
        profile = CustomerProfile.objects.get(user=user)
        self.assertEqual(profile.first_name, 'Test')
        self.assertEqual(profile.last_name, 'Customer')

    def test_password_reset_request_success(self):
        """Test successful password reset request"""
        data = {
            'email': 'verified@example.com'
        }
        response = self.client.post(self.password_reset_request_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify reset token was created
        self.assertTrue(
            PasswordReset.objects.filter(user=self.verified_customer).exists()
        )

    def test_password_reset_request_invalid_email(self):
        """Test password reset request with invalid email"""
        data = {
            'email': 'nonexistent@example.com'
        }
        response = self.client.post(self.password_reset_request_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', str(response.data))

    def test_password_reset_confirm_success(self):
        """Test successful password reset confirmation"""
        # Create password reset token
        reset_token = PasswordReset.objects.create(
            user=self.verified_customer,
            expires_at=timezone.now() + timezone.timedelta(hours=24)
        )
        
        data = {
            'token': str(reset_token.token),
            'email': self.verified_customer.email,
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        
        response = self.client.post(self.password_reset_confirm_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password reset successful')
        
        # Verify password was changed
        self.verified_customer.refresh_from_db()
        self.assertTrue(self.verified_customer.check_password('newpass123'))
        
        # Verify token was marked as used
        reset_token.refresh_from_db()
        self.assertIsNotNone(reset_token.used_at)

    def test_password_reset_confirm_invalid_token(self):
        """Test password reset confirmation with invalid token"""
        data = {
            'token': str(uuid.uuid4()),  # Random invalid token
            'email': self.verified_customer.email,
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        
        response = self.client.post(self.password_reset_confirm_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', str(response.data))

    def test_password_reset_confirm_passwords_mismatch(self):
        """Test password reset confirmation with mismatched passwords"""
        reset_token = PasswordReset.objects.create(
            user=self.verified_customer,
            expires_at=timezone.now() + timezone.timedelta(hours=24)
        )
        
        data = {
            'token': str(reset_token.token),
            'email': self.verified_customer.email,
            'new_password': 'newpass123',
            'confirm_password': 'differentpass123'
        }
        
        response = self.client.post(self.password_reset_confirm_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Passwords don\'t match', str(response.data))

    def test_password_reset_confirm_expired_token(self):
        """Test password reset confirmation with expired token"""
        # Create expired reset token
        reset_token = PasswordReset.objects.create(
            user=self.verified_customer,
            expires_at=timezone.now() - timezone.timedelta(hours=1)  # Expired
        )
        
        data = {
            'token': str(reset_token.token),
            'email': self.verified_customer.email,
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        
        response = self.client.post(self.password_reset_confirm_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('expired', str(response.data).lower())