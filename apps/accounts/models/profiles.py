from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class BaseProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='%(class)s'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class GlobalBuyerProfile(BaseProfile):
    VERIFICATION_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    company_name = models.CharField(max_length=255)
    business_registration_number = models.CharField(max_length=100)
    tax_id = models.CharField(max_length=100)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='PENDING'
    )
    credit_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    company_address = models.TextField()
    company_website = models.URLField(blank=True)
    contact_person = models.CharField(max_length=255)

    class Meta:
        verbose_name = _('Global Buyer Profile')
        verbose_name_plural = _('Global Buyer Profiles')

    def __str__(self):
        return f"{self.company_name} - {self.verification_status}"

class VendorProfile(BaseProfile):
    VERIFICATION_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    store_name = models.CharField(max_length=255)
    store_description = models.TextField()
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='PENDING'
    )
    bank_account_name = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100)
    store_address = models.TextField()
    store_phone = models.CharField(max_length=15)

    class Meta:
        verbose_name = _('Vendor Profile')
        verbose_name_plural = _('Vendor Profiles')

    def __str__(self):
        return f"{self.store_name} - {self.verification_status}"

class CustomerProfile(BaseProfile):
    shipping_address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    newsletter_subscription = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _('Customer Profile')
        verbose_name_plural = _('Customer Profiles')

    def __str__(self):
        return f"Customer Profile - {self.user.email}"
