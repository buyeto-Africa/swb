# Generated by Django 5.1.4 on 2024-12-15 16:25

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0004_remove_customerprofile_address_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerSupportTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('open', 'Open'), ('in_progress', 'In Progress'), ('resolved', 'Resolved'), ('closed', 'Closed')], default='open', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerWishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-added_at'],
            },
        ),
        migrations.AddField(
            model_name='customeraddress',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='customeraddress',
            name='address_type',
            field=models.CharField(choices=[('home', 'Home'), ('work', 'Work'), ('other', 'Other')], default='home', max_length=10),
        ),
        migrations.CreateModel(
            name='CustomerOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=50, unique=True)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.customerprofile')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CustomerPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_preferences', models.JSONField(default=dict)),
                ('language_preference', models.CharField(default='en', max_length=10)),
                ('currency_preference', models.CharField(choices=[('USD', 'US Dollar'), ('EUR', 'Euro'), ('GBP', 'British Pound')], default='USD', max_length=3)),
                ('customer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='preferences', to='customer.customerprofile')),
            ],
            options={
                'verbose_name_plural': 'Customer preferences',
            },
        ),
        migrations.CreateModel(
            name='CustomerReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('review_text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='customer.customerprofile')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
