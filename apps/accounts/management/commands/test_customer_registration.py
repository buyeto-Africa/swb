import json
import requests
import time
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Command(BaseCommand):
    help = 'Test customer registration flow'

    def handle(self, *args, **options):
        # Test data
        registration_data = {
            'email': f'customer_{int(time.time())}@example.com',  # Generate unique email using timestamp
            'first_name': 'John',
            'last_name': 'Smith',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'phone_number': '+1234567890',
            'shipping_address': '123 Main St, City, Country',
            'billing_address': '123 Main St, City, Country',
            'newsletter_subscription': True
        }

        # Base URL for API endpoints
        base_url = 'http://localhost:8000/api/accounts'

        # Step 1: Register the customer
        register_url = f'{base_url}/register/customer/'
        register_response = requests.post(register_url, json=registration_data)

        if register_response.status_code == 201:
            self.stdout.write(self.style.SUCCESS('Registration successful!'))
            self.stdout.write(json.dumps(register_response.json(), indent=2))
        else:
            self.stdout.write(self.style.ERROR('Registration failed!'))
            self.stdout.write(json.dumps(register_response.json(), indent=2))
            return

        # Step 2: Login with the registered credentials
        login_url = f'{base_url}/login/'
        login_data = {
            'email': registration_data['email'],
            'password': registration_data['password']
        }
        login_response = requests.post(login_url, json=login_data)

        if login_response.status_code == 200:
            self.stdout.write(self.style.SUCCESS('Login successful!'))
            tokens = login_response.json()
            self.stdout.write(f'Access Token: {tokens["access"]}')
            self.stdout.write(f'Refresh Token: {tokens["refresh"]}')
        else:
            self.stdout.write(self.style.ERROR('Login failed!'))
            self.stdout.write(json.dumps(login_response.json(), indent=2))
            return

        # Step 3: Logout
        logout_url = f'{base_url}/logout/'
        headers = {'Authorization': f'Bearer {tokens["access"]}'}
        logout_data = {'refresh': tokens['refresh']}  # Add refresh token to request body
        logout_response = requests.post(logout_url, json=logout_data, headers=headers)

        if logout_response.status_code == 205:
            self.stdout.write(self.style.SUCCESS('Logout successful!'))
        else:
            self.stdout.write(self.style.ERROR('Logout failed!'))
            if logout_response.content:  # Only try to parse JSON if there's content
                try:
                    self.stdout.write(json.dumps(logout_response.json(), indent=2))
                except json.JSONDecodeError:
                    self.stdout.write(f'Status code: {logout_response.status_code}')
                    self.stdout.write(f'Response text: {logout_response.text}')
