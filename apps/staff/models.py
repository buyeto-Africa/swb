# apps/staff/models.py

from django.db import models
from django.utils import timezone
from apps.userauths.models import User
import uuid
from django.dispatch import receiver
from django.db.models.signals import post_save

class StaffRole(models.Model):
    name = models.CharField(max_length=100, unique=True)
    permissions = models.JSONField(default=dict)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def staff_count(self):
        return self.staffprofile_set.count()

    def get_permissions_display(self):
        return ", ".join(self.permissions.get('allowed_actions', []))

class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    role = models.ForeignKey(StaffRole, on_delete=models.PROTECT, related_name='staffprofile_set')
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"

    def has_permission(self, permission):
        if not self.is_active:
            return False
        return permission in self.role.permissions.get('allowed_actions', [])

    def update_last_login(self):
        self.last_login = timezone.now()
        self.save()

class StaffInvitation(models.Model):
    email = models.EmailField(unique=True)
    role = models.ForeignKey(StaffRole, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    attempts = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Invitation for {self.email} - {self.role.name}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def can_be_used(self):
        return not self.is_accepted and not self.is_expired

    def mark_as_used(self):
        self.is_accepted = True
        self.accepted_at = timezone.now()
        self.save()

    def increment_attempts(self):
        self.attempts += 1
        self.save()

@receiver(post_save, sender=User)
def create_staff_profile(sender, instance, created, **kwargs):
    if created and instance.user_type == 'staff':
        default_role = StaffRole.objects.get_or_create(
            name="Basic Staff",
            defaults={
                'permissions': {
                    'allowed_actions': ['view_basic_info']
                },
                'description': 'Basic staff role with minimal permissions'
            }
        )[0]
        StaffProfile.objects.create(
            user=instance,
            role=default_role
        )