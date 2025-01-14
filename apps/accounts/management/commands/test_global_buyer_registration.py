from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import UserInvitation
import requests
import json

User = get_user_model()

class Command(BaseCommand):
    help = 'Test Global Buyer registration and logout process'

    def handle(self, *args, **kwargs):
        # Create admin user if doesn't exist
        admin_email = 'admin@example.com'
        admin_password = 'admin123!@#'
        buyer_email = 'buyer@example.com'
        
        # Clean up existing test data
        UserInvitation.objects.filter(email__in=[admin_email, buyer_email]).delete()
        User.objects.filter(email__in=[admin_email, buyer_email]).delete()
        
        # Create admin user
        admin_user = User.objects.create_superuser(
            email=admin_email,
            password=admin_password,
            user_type=User.UserType.ADMIN,
            is_active=True
        )
        self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_email}'))
        
        # Create invitation for global buyer
        invitation = UserInvitation.objects.create(
            email=buyer_email,
            user_type=User.UserType.GLOBAL_BUYER,
            invited_by=admin_user
        )
        self.stdout.write(self.style.SUCCESS(f'Created invitation for: {buyer_email}'))
        self.stdout.write(f'Invitation token: {invitation.token}')
        
        # Test registration
        registration_data = {
            'email': buyer_email,
            'password': 'buyer123!@#',
            'password_confirm': 'buyer123!@#',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+1234567890',
            'company_name': 'Global Trading Co',
            'business_registration_number': 'BRN123456',
            'tax_id': 'TAX123456',
            'company_address': '123 Global Street, Business City',
            'contact_person': 'John Doe',
            'invitation_token': str(invitation.token)
        }
        
        response = requests.post(
            'http://localhost:8000/api/accounts/register/invited/',
            json=registration_data
        )
        
        if response.status_code == 201:
            self.stdout.write(self.style.SUCCESS('Registration successful!'))
            self.stdout.write(json.dumps(response.json(), indent=2))
            
            # Test login to get tokens
            login_data = {
                'email': buyer_email,
                'password': 'buyer123!@#'
            }
            
            login_response = requests.post(
                'http://localhost:8000/api/accounts/login/',
                json=login_data
            )
            
            if login_response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('Login successful!'))
                tokens = login_response.json()
                
                # Test logout
                logout_data = {
                    'refresh': tokens['refresh']
                }
                
                headers = {
                    'Authorization': f'Bearer {tokens["access"]}'
                }
                
                # Print tokens for debugging
                self.stdout.write(f'Access Token: {tokens["access"]}')
                self.stdout.write(f'Refresh Token: {tokens["refresh"]}')
                
                logout_response = requests.post(
                    'http://localhost:8000/api/accounts/logout/',
                    json=logout_data,
                    headers=headers
                )
                
                if logout_response.status_code == 205:
                    self.stdout.write(self.style.SUCCESS('Logout successful!'))
                else:
                    self.stdout.write(self.style.ERROR('Logout failed!'))
                    self.stdout.write(f'Status code: {logout_response.status_code}')
                    self.stdout.write(f'Response: {logout_response.text}')
            else:
                self.stdout.write(self.style.ERROR('Login failed!'))
                self.stdout.write(f'Status code: {login_response.status_code}')
                self.stdout.write(f'Response: {login_response.text}')
        else:
            self.stdout.write(self.style.ERROR('Registration failed!'))
            self.stdout.write(f'Status code: {response.status_code}')
            self.stdout.write(f'Response: {response.text}')
