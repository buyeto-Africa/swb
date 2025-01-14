from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models.user import User
from apps.accounts.models.invitation import UserInvitation
import requests
import logging
import json

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test vendor registration flow'

    def handle(self, *args, **kwargs):
        # Get or create admin user for testing
        User = get_user_model()
        admin_email = 'admin@example.com'
        admin_password = 'testpass123'

        admin_user, created = User.objects.get_or_create(
            email=admin_email,
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password(admin_password)
            admin_user.save()
            self.stdout.write(f'Created admin user: {admin_email}')
        else:
            self.stdout.write(f'Using existing admin user: {admin_email}')

        # Clean up any existing test vendor
        User.objects.filter(email='vendor@example.com').delete()
        UserInvitation.objects.filter(email='vendor@example.com').delete()

        # Test data for vendor
        vendor_email = 'vendor@example.com'
        vendor_data = {
            'email': vendor_email,
            'first_name': 'John',
            'last_name': 'Smith',
            'phone_number': '+1234567890',
            'company_name': 'Test Vendor Company',
            'company_address': '123 Vendor Street',
            'company_registration_number': 'VEN123456',
            'tax_id': 'TAX123456',
            'business_type': 'Corporation'
        }

        # Create invitation for vendor
        invitation = UserInvitation.objects.create(
            email=vendor_email,
            user_type=User.UserType.VENDOR,
            invited_by=admin_user
        )
        
        # Send invitation email
        invitation.send_invitation_email()
        self.stdout.write(f'Created invitation for: {vendor_email}')
        self.stdout.write(f'Invitation token: {invitation.token}')

        # Test registration with the invitation token
        registration_data = {
            **vendor_data,
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'invitation_token': str(invitation.token)
        }

        # Make registration request
        response = requests.post(
            'http://localhost:8000/api/accounts/register/invited/',
            json=registration_data
        )

        if response.status_code == 201:
            self.stdout.write('Registration successful!')
            self.stdout.write(json.dumps(response.json(), indent=2))
        else:
            self.stdout.write(self.style.ERROR(f'Registration failed: {response.text}'))
            return

        # Test login
        login_data = {
            'email': vendor_email,
            'password': 'testpass123'
        }

        response = requests.post(
            'http://localhost:8000/api/accounts/login/',
            json=login_data
        )

        if response.status_code == 200:
            self.stdout.write('Login successful!')
            tokens = response.json()
            self.stdout.write(f'Access Token: {tokens["access"]}')
            self.stdout.write(f'Refresh Token: {tokens["refresh"]}')

            # Test logout
            headers = {'Authorization': f'Bearer {tokens["access"]}'}
            logout_data = {'refresh': tokens['refresh']}
            
            response = requests.post(
                'http://localhost:8000/api/accounts/logout/',
                json=logout_data,
                headers=headers
            )

            if response.status_code in [200, 204, 205]:
                self.stdout.write('Logout successful!')
            else:
                self.stdout.write(self.style.ERROR(f'Logout failed: {response.text}'))
        else:
            self.stdout.write(self.style.ERROR(f'Login failed: {response.text}'))
