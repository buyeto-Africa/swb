# apps/userauths/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid
from datetime import timedelta
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        extra_fields.setdefault('is_email_verified', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('staff', 'Staff')
    )


    

    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.'
    )

    username = models.CharField(max_length=100, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'"
    )
    phone = models.CharField(validators=[phone_regex], max_length=15)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(null=True, blank=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    # ... (keep existing methods)




    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split('@')[0]

        if not self.is_email_verified and not self.email_verification_token:
            self.email_verification_token = uuid.uuid4()

        super().save(*args, **kwargs)
        

    def __str__(self):
        return self.email

    # def save(self, *args, **kwargs):
    #     if not self.username:
    #         self.username = self.email.split('@')[0]
    #     super().save(*args, **kwargs)

    # def __str__(self):
    #     return self.email

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Invitation(models.Model):
    INVITATION_TYPE_CHOICES = (
        ('vendor', 'Vendor'),
        ('staff', 'Staff')
    )

    email = models.EmailField(unique=True)
    invitation_type = models.CharField(max_length=10, choices=INVITATION_TYPE_CHOICES)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    business_name = models.CharField(max_length=255, null=True, blank=True)  # For vendors
    role = models.CharField(max_length=100, null=True, blank=True)  # For staff
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    invited_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='sent_invitations'
    )

    def __str__(self):
        return f"{self.invitation_type} invitation for {self.email}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Set expiration to 7 days from creation
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    class Meta:
        verbose_name = 'Invitation'
        verbose_name_plural = 'Invitations'


# apps/userauths/models.py

# apps/userauths/models.py

from django.db import models
from django.utils import timezone
import uuid

# ... existing User model code ...

# apps/userauths/models.py

from django.db import models
from django.utils import timezone
from django.core.cache import cache
import uuid

# apps/userauths/models.py

from django.db import models
from django.utils import timezone
from django.core.cache import cache
import uuid

# apps/userauths/models.py

from django.db import models
from django.utils import timezone
from django.core.cache import cache
import uuid

# class PasswordReset(models.Model):
#     user = models.ForeignKey('User', on_delete=models.CASCADE)
#     token = models.UUIDField(default=uuid.uuid4, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     used_at = models.DateTimeField(null=True, blank=True)
#     expires_at = models.DateTimeField()




#     def save(self, *args, **kwargs):
#         if not self.expires_at:
#             # Set default expiration to 24 hours from creation
#             self.expires_at = timezone.now() + timedelta(hours=24)
#         super().save(*args, **kwargs)


#     @classmethod
#     def check_rate_limit(cls, email):
#         """Check if user has exceeded rate limit"""
#         cache_key = f"password_reset_count_{email}"
#         count = cache.get(cache_key, 0)
#         return count >= 3  # Limit to 3 requests per hour

#     @classmethod
#     def increment_request_count(cls, email):
#         """Increment request count for rate limiting"""
#         cache_key = f"password_reset_count_{email}"
#         count = cache.get(cache_key, 0)
#         cache.set(cache_key, count + 1, 3600)  # 1 hour expiry


# apps/userauths/models.py

class PasswordReset(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Set expiration to 24 hours from creation by default
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at or self.used_at is not None

    class Meta:
        verbose_name = 'Password Reset'
        verbose_name_plural = 'Password Resets'