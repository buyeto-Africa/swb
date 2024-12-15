# apps/vendors/models.py

from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.userauths.models import User
import uuid


# apps/vendors/models.py

from django.db import models
from django.utils import timezone
from apps.userauths.models import User
import uuid

class VendorInvitation(models.Model):
    email = models.EmailField(unique=True)
    business_name = models.CharField(max_length=200)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)

    class Meta:
        verbose_name = 'Vendor Invitation'
        verbose_name_plural = 'Vendor Invitations'

    def __str__(self):
        return f"Invitation for {self.email}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)

    @property
    def can_be_used(self):
        """Check if invitation is valid and can be used"""
        return (
            not self.is_accepted and 
            not self.is_expired and 
            self.attempts < self.max_attempts
        )

    def increment_attempts(self):
        """Track failed attempts to use invitation"""
        self.attempts += 1
        self.save()






class VendorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    business_name = models.CharField(max_length=200)
    business_description = models.TextField(null=True, blank=True)
    business_address = models.TextField(null=True, blank=True)
    business_phone = models.CharField(max_length=15, null=True, blank=True)
    business_email = models.EmailField(null=True, blank=True)
    registration_number = models.CharField(max_length=100, null=True, blank=True)
    tax_id = models.CharField(max_length=100, null=True, blank=True)
    logo = models.ImageField(upload_to='vendors/logos/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business_name} - {self.user.email}"





    # apps/vendor/models.py

# @receiver(post_save, sender=User)
# def create_vendor_profile(sender, instance, created, **kwargs):
#     # Only create profile if one doesn't already exist
#     if created and instance.user_type == 'vendor' and not hasattr(instance, 'vendor_profile'):
#         VendorProfile.objects.create(
#             user=instance,
#             business_name=instance.email.split('@')[0]  # Default business name
#         )