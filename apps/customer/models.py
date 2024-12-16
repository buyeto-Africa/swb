from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.constants import SUPPORTED_CURRENCIES
from apps.core.mixins import TimestampMixin
from apps.core.services.currency import CurrencyConverter
from django.db import models
from django.conf import settings
from apps.product.models import Product

# Create your models here.
# apps/customers/models.py

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.userauths.models import User
import uuid

class CustomerProfile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='customers/profile_pics/', null=True, blank=True)
    phone_verified = models.BooleanField(default=False)
    email_preferences = models.JSONField(default=dict)
    notification_preferences = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_profile'

    def __str__(self):
        return f"{self.user.email}'s Profile"

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.user.email.split('@')[0]

# Signal to create customer profile when user is created
@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    if created and instance.user_type == 'customer':
         CustomerProfile.objects.create(
            user=instance,
            first_name=instance.first_name if hasattr(instance, 'first_name') else '',
            last_name=instance.last_name if hasattr(instance, 'last_name') else ''
        )
         


class CustomerAddress(models.Model):
    ADDRESS_TYPES = (
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other')
    )

    customer = models.ForeignKey(
        'CustomerProfile', 
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    address_type = models.CharField(
        max_length=10, 
        choices=ADDRESS_TYPES,
        default='home'
    )
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name_plural = 'Customer addresses'

    def save(self, *args, **kwargs):
        # If this is being set as default, remove default from other addresses
        if self.is_default:
            CustomerAddress.objects.filter(
                customer=self.customer,
                is_default=True
            ).update(is_default=False)
        super().save(*args, **kwargs)






class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at






# apps/customers/models.py

# apps/customer/models.py

from django.db import models

class CustomerPreferences(models.Model):
    customer = models.OneToOneField('CustomerProfile', on_delete=models.CASCADE, related_name='preferences')
    notification_preferences = models.JSONField(default=dict)
    language_preference = models.CharField(max_length=10, default='en')
    currency_preference = models.CharField(
        max_length=3,
        choices=[
            ('USD', 'US Dollar'),
            ('EUR', 'Euro'),
            ('GBP', 'British Pound'),
            # Add more currencies as needed
        ],
        default='USD'
    )

    class Meta:
        verbose_name_plural = 'Customer preferences'

    def __str__(self):
        return f"{self.customer.user.email}'s preferences"







class CustomerOrder(models.Model):
    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    )

    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey('CustomerProfile', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_number} by {self.customer.user.email}"

    class Meta:
        ordering = ['-created_at']








class CustomerWishlist(models.Model):
    customer = models.ForeignKey('CustomerProfile', on_delete=models.CASCADE, related_name='wishlists')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['customer', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.customer.user.email}'s wishlist item - {self.product.name}"






# apps/customers/models.py

# apps/customer/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomerReview(models.Model):
    customer = models.ForeignKey('CustomerProfile', on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['customer', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.customer.user.email} for {self.product.name}"


    

# apps/customers/models.py

class CustomerSupportTicket(models.Model):
    TICKET_STATUS = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    )
    
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=TICKET_STATUS, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)