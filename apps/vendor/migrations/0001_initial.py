# Generated by Django 5.1.4 on 2024-12-13 23:49

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('userauths', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('business_name', models.CharField(max_length=200)),
                ('token', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('is_accepted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('accepted_at', models.DateTimeField(blank=True, null=True)),
                ('attempts', models.IntegerField(default=0)),
                ('invited_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='userauths.user')),
            ],
        ),
        migrations.CreateModel(
            name='VendorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_name', models.CharField(max_length=200)),
                ('business_description', models.TextField(blank=True, null=True)),
                ('business_address', models.TextField()),
                ('business_phone', models.CharField(max_length=15)),
                ('business_email', models.EmailField(max_length=254)),
                ('registration_number', models.CharField(blank=True, max_length=100, null=True)),
                ('tax_id', models.CharField(blank=True, max_length=100, null=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='vendors/logos/')),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_profile', to='userauths.user')),
            ],
        ),
    ]