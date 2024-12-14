# apps/vendors/models.py
from django.db import models
from django.utils import timezone
from apps.userauths.models import User
import uuid

from django.db.models.signals import post_save
from django.dispatch import receiver



class VendorInvitation(models.Model):
    email = models.EmailField(unique=True)
    business_name = models.CharField(max_length=200)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    attempts = models.IntegerField(default=0)  # Track invalid attempts

    def save(self, *args, **kwargs):
        # Set default expiration to 7 days if not set
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invitation for {self.email}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def can_be_used(self):
        """Check if invitation is valid and can be used"""
        return not self.is_accepted and not self.is_expired

    def mark_as_used(self):
        """Mark invitation as accepted and record time"""
        self.is_accepted = True
        self.accepted_at = timezone.now()
        self.save()

    def increment_attempts(self):
        """Track failed attempts to use invitation"""
        self.attempts += 1
        self.save()



class VendorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    business_name = models.CharField(max_length=200)
    business_description = models.TextField(null=True, blank=True)
    business_address = models.TextField()
    business_phone = models.CharField(max_length=15)
    business_email = models.EmailField()
    registration_number = models.CharField(max_length=100, null=True, blank=True)
    tax_id = models.CharField(max_length=100, null=True, blank=True)
    logo = models.ImageField(upload_to='vendors/logos/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name

# Signal to create vendor profile when vendor user is created
@receiver(post_save, sender=User)
def create_vendor_profile(sender, instance, created, **kwargs):
    if created and instance.user_type == 'vendor':
        VendorProfile.objects.create(
            user=instance,
            business_email=instance.email,
            business_phone=instance.phone
        )