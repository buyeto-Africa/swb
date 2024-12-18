# Generated by Django 5.1.4 on 2024-12-14 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0002_alter_vendorinvitation_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vendorprofile',
            options={},
        ),
        migrations.RemoveField(
            model_name='vendorprofile',
            name='verification_notes',
        ),
        migrations.RemoveField(
            model_name='vendorprofile',
            name='verification_status',
        ),
        migrations.AddField(
            model_name='vendorprofile',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='vendorprofile',
            name='business_address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vendorprofile',
            name='business_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='vendorprofile',
            name='business_phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
