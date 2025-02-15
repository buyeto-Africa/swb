# Generated by Django 5.1.4 on 2025-01-11 22:12

import apps.accounts.models.invitation
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_is_verified_user_phone_number_user_user_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, verbose_name='email address')),
                ('user_type', models.CharField(choices=[('ADMIN', 'Administrator'), ('STORE_MANAGER', 'Store Manager'), ('FULFILLMENT_SPECIALIST', 'Fulfillment Specialist'), ('SUPPORT_AGENT', 'Support Agent'), ('WAREHOUSE_STAFF', 'Warehouse Staff'), ('ACCOUNTANT', 'Accountant'), ('B2B_PARTNER', 'B2B Partner'), ('VENDOR', 'Vendor'), ('CUSTOMER', 'Customer')], max_length=50, validators=[apps.accounts.models.invitation.validate_non_customer], verbose_name='user type')),
                ('token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('is_used', models.BooleanField(default=False)),
                ('invited_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invitations_sent', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user invitation',
                'verbose_name_plural': 'user invitations',
                'unique_together': {('email', 'user_type', 'is_used')},
            },
        ),
    ]
