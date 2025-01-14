from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', User.UserType.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class UserType(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        STORE_MANAGER = 'STORE_MANAGER', _('Store Manager')
        FULFILLMENT_SPECIALIST = 'FULFILLMENT_SPECIALIST', _('Fulfillment Specialist')
        SUPPORT_AGENT = 'SUPPORT_AGENT', _('Support Agent')
        WAREHOUSE_STAFF = 'WAREHOUSE_STAFF', _('Warehouse Staff')
        ACCOUNTANT = 'ACCOUNTANT', _('Accountant')
        GLOBAL_BUYER = 'GLOBAL_BUYER', _('Global Buyer')
        VENDOR = 'VENDOR', _('Vendor')
        CUSTOMER = 'CUSTOMER', _('Customer')

    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    user_type = models.CharField(
        _('user type'),
        max_length=50,
        choices=UserType.choices,
        default=UserType.CUSTOMER
    )
    company_name = models.CharField(_('company name'), max_length=255, blank=True)
    is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_('Designates whether this user has completed the verification process.'),
    )
    is_approved = models.BooleanField(
        _('approved'),
        default=False,
        help_text=_('Designates whether this user has been approved by an admin.')
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_login = models.DateTimeField(_('last login'), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        
    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        pass  # TODO: Implement email sending functionality

    @property
    def is_platform_staff(self):
        """Check if user is any type of platform staff."""
        return self.user_type in [
            self.UserType.ADMIN,
            self.UserType.STORE_MANAGER,
            self.UserType.FULFILLMENT_SPECIALIST,
            self.UserType.SUPPORT_AGENT,
            self.UserType.WAREHOUSE_STAFF,
            self.UserType.ACCOUNTANT,
        ]

    @property
    def is_global_buyer(self):
        """Check if user is a Global Buyer."""
        return self.user_type == self.UserType.GLOBAL_BUYER

    @property
    def is_vendor(self):
        """Check if user is a vendor."""
        return self.user_type == self.UserType.VENDOR

    @property
    def is_customer(self):
        """Check if user is a customer."""
        return self.user_type == self.UserType.CUSTOMER
