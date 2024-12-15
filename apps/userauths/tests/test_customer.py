# apps/userauths/tests/test_customer.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.userauths.models import User
from apps.customer.models import CustomerProfile

class CustomerRegistrationTests(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.customer_register_url = reverse('auth-customer-register')
        self.valid_customer_data = {
            'email': 'customer@example.com',
            'phone': '+1234567890',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'Customer'
        }

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

    def test_duplicate_email_registration(self):
        """Test registration with existing email"""
        # First create a user
        User.objects.create_user(
            email='customer@example.com',
            phone='+9876543210',
            password='existingpass123',
            user_type='customer'
        )

        response = self.client.post(
            self.customer_register_url,
            self.valid_customer_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['error'])
        self.assertIn('already exists', str(response.data['error']))

    def test_invalid_phone_number(self):
        """Test registration with invalid phone number"""
        invalid_data = self.valid_customer_data.copy()
        invalid_data['phone'] = '123'  # Invalid phone format

        response = self.client.post(
            self.customer_register_url,
            invalid_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.data)
        self.assertIn('+999999999', str(response.data['phone'][0]))

    def test_missing_required_fields(self):
        """Test registration with missing required fields"""
        invalid_data = {
            'email': 'customer@example.com'
            # Missing other required fields
        }

        response = self.client.post(
            self.customer_register_url,
            invalid_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data['error'])
        self.assertIn('phone', response.data['error'])
        self.assertIn('first_name', response.data['error'])
        self.assertIn('last_name', response.data['error'])


   
        