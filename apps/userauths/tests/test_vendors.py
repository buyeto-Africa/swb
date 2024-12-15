# # apps/userauths/tests/test_vendors.py

# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from django.utils import timezone
# from apps.userauths.models import User
# from apps.vendor.models import VendorInvitation, VendorProfile

# class VendorAuthenticationTests(APITestCase):
#     def setUp(self):
#         """Set up test data"""
#         # Create admin user
#         self.admin = User.objects.create_superuser(
#             email='admin@example.com',
#             phone='+1234567890',
#             password='adminpass123'
#         )

#         # Create URLs
#         self.vendor_register_url = reverse('auth-vendor-register')

#         # Create vendor invitation
#         self.vendor_invitation = VendorInvitation.objects.create(
#             email='vendor@example.com',
#             business_name='Test Vendor',
#             invited_by=self.admin,
#             expires_at=timezone.now() + timezone.timedelta(days=7)
#         )

#     def test_vendor_registration_success(self):
#         """Test successful vendor registration with valid invitation"""
#         data = {
#             'email': 'vendor@example.com',
#             'phone': '+1234567891',
#             'password': 'testpass123',
#             'invitation_token': str(self.vendor_invitation.token),
#             'business_name': 'Test Vendor'
#         }

#         # Print request data for debugging
#         print("Request Data:", data)
        
#         response = self.client.post(self.vendor_register_url, data, format='json')
        
#         # Print response data for debugging
#         print("Response Status:", response.status_code)
#         print("Response Data:", response.data)

#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertIn('message', response.data)
#         self.assertIn('email', response.data)

#         # Verify user was created
#         user = User.objects.get(email='vendor@example.com')
#         self.assertEqual(user.user_type, 'vendor')
#         self.assertTrue(user.is_email_verified)

#         # Verify vendor profile was created
#         vendor_profile = VendorProfile.objects.get(user=user)
#         self.assertEqual(vendor_profile.business_name, 'Test Vendor')

#         # Verify invitation was marked as accepted
#         invitation = VendorInvitation.objects.get(token=self.vendor_invitation.token)
#         self.assertTrue(invitation.is_accepted)





# apps/userauths/tests/test_vendors.py

# from django.test import TestCase
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from django.utils import timezone
# from apps.userauths.models import User
# from apps.vendor.models import VendorInvitation
# import uuid

# class VendorAuthenticationTests(APITestCase):
#     def setUp(self):
#         """Set up test data"""
#         # Create admin user
#         self.admin = User.objects.create_superuser(
#             email='admin@example.com',
#             phone='+1234567890',
#             password='adminpass123'
#         )

#         # Create URLs
#         self.vendor_register_url = reverse('auth-vendor-register')

#         # Create valid invitation
#         self.valid_invitation = VendorInvitation.objects.create(
#             email='vendor@example.com',
#             business_name='Test Vendor',
#             invited_by=self.admin,
#             expires_at=timezone.now() + timezone.timedelta(days=7)
#         )

#         # Create expired invitation
#         self.expired_invitation = VendorInvitation.objects.create(
#             email='expired@example.com',
#             business_name='Expired Vendor',
#             invited_by=self.admin,
#             expires_at=timezone.now() - timezone.timedelta(days=1)
#         )

#         # Create used invitation
#         self.used_invitation = VendorInvitation.objects.create(
#             email='used@example.com',
#             business_name='Used Vendor',
#             invited_by=self.admin,
#             expires_at=timezone.now() + timezone.timedelta(days=7),
#             is_accepted=True
#         )

#     def test_vendor_registration_success(self):
#         """Test successful vendor registration with valid invitation"""
#         data = {
#             'email': 'vendor@example.com',
#             'phone': '+1234567891',
#             'password': 'testpass123',
#             'invitation_token': str(self.valid_invitation.token),
#             'business_name': 'Test Vendor'
#         }
#         response = self.client.post(self.vendor_register_url, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data['message'], 'Vendor registration successful')
#         self.assertEqual(response.data['email'], 'vendor@example.com')

#     def test_invalid_invitation_token(self):
#         """Test registration with invalid invitation token"""
#         data = {
#             'email': 'vendor@example.com',
#             'phone': '+1234567891',
#             'password': 'testpass123',
#             'invitation_token': str(uuid.uuid4()),  # Random invalid token
#             'business_name': 'Test Vendor'
#         }
#         response = self.client.post(self.vendor_register_url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['error'], 'Invalid invitation')

#     def test_expired_invitation(self):
#         """Test registration with expired invitation"""

#         self.valid_invitation.expires_at = timezone.now() - timezone.timedelta(days=1)
#         self.valid_invitation.save()

#         data = {
#             'email': 'expired@example.com',
#             'phone': '+1234567891',
#             'password': 'testpass123',
#             'invitation_token': str(self.expired_invitation.token),
#             'business_name': 'Expired Vendor'
#         }
#         response = self.client.post(self.vendor_register_url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['error'], 'Invitation has expired')

#     def test_already_used_invitation(self):
#         """Test registration with already used invitation"""

#         self.vendor_invitation.is_accepted = True
#         self.vendor_invitation.save()

#         data = {
#             'email': 'used@example.com',
#             'phone': '+1234567891',
#             'password': 'testpass123',
#             'invitation_token': str(self.used_invitation.token),
#             'business_name': 'Used Vendor'
#         }
#         response = self.client.post(self.vendor_register_url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['error'], 'Invitation has already been used')

#     def test_missing_required_fields(self):
#         """Test registration with missing required fields"""
#         # Test missing email
#         data = {
#             'phone': '+1234567891',
#             'password': 'testpass123',
#             'invitation_token': str(self.valid_invitation.token),
#             'business_name': 'Test Vendor'
#         }
#         response = self.client.post(self.vendor_register_url, data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('email', response.data)

#         # Test missing business name
#         data = {
#             'email': 'vendor@example.com',
#             'phone': '+1234567891',
#             'password': 'testpass123',
#             'invitation_token': str(self.valid_invitation.token)
#         }
#         response = self.client.post(self.vendor_register_url, data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('business_name', response.data)



# apps/userauths/tests/test_vendors.py

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from apps.userauths.models import User
from apps.vendor.models import VendorInvitation
import uuid

class VendorAuthenticationTests(APITestCase):
    def setUp(self):
        """Set up test data"""
        # Create admin user
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            phone='+1234567890',
            password='adminpass123'
        )

        # Create URLs
        self.vendor_register_url = reverse('auth-vendor-register')

        # Create vendor invitation
        self.vendor_invitation = VendorInvitation.objects.create(
            email='vendor@example.com',
            business_name='Test Vendor',
            invited_by=self.admin,
            expires_at=timezone.now() + timezone.timedelta(days=7)
        )

    def test_vendor_registration_success(self):
        """Test successful vendor registration with valid invitation"""
        data = {
            'email': 'vendor@example.com',
            'phone': '+1234567891',
            'password': 'testpass123',
            'invitation_token': str(self.vendor_invitation.token),
            'business_name': 'Test Vendor'
        }
        response = self.client.post(self.vendor_register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Vendor registration successful')
        self.assertEqual(response.data['email'], 'vendor@example.com')

    def test_invalid_invitation_token(self):
        """Test registration with invalid invitation token"""
        data = {
            'email': 'vendor@example.com',
            'phone': '+1234567891',
            'password': 'testpass123',
            'invitation_token': str(uuid.uuid4()),
            'business_name': 'Test Vendor'
        }
        response = self.client.post(self.vendor_register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid invitation')

    def test_expired_invitation(self):
        """Test registration with expired invitation"""
        # Update invitation to be expired
        self.vendor_invitation.expires_at = timezone.now() - timezone.timedelta(days=1)
        self.vendor_invitation.save()

        data = {
            'email': 'vendor@example.com',
            'phone': '+1234567891',
            'password': 'testpass123',
            'invitation_token': str(self.vendor_invitation.token),
            'business_name': 'Test Vendor'
        }
        response = self.client.post(self.vendor_register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invitation has expired')

    def test_already_used_invitation(self):
        """Test registration with already used invitation"""
        # Mark invitation as accepted
        self.vendor_invitation.is_accepted = True
        self.vendor_invitation.save()

        data = {
            'email': 'vendor@example.com',
            'phone': '+1234567891',
            'password': 'testpass123',
            'invitation_token': str(self.vendor_invitation.token),
            'business_name': 'Test Vendor'
        }
        response = self.client.post(self.vendor_register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invitation has already been used')

    def test_missing_required_fields(self):
        """Test registration with missing required fields"""
        data = {
            'invitation_token': str(self.vendor_invitation.token),
            'business_name': 'Test Vendor'
        }
        response = self.client.post(self.vendor_register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('This field is required', str(response.data['error']))