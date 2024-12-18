# Generated by Django 5.1.4 on 2024-12-14 04:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vendorinvitation',
            options={'verbose_name': 'Vendor Invitation', 'verbose_name_plural': 'Vendor Invitations'},
        ),
        migrations.AlterModelOptions(
            name='vendorprofile',
            options={'ordering': ['-created_at'], 'verbose_name': 'Vendor Profile', 'verbose_name_plural': 'Vendor Profiles'},
        ),
        migrations.RemoveField(
            model_name='vendorprofile',
            name='is_verified',
        ),
        migrations.AddField(
            model_name='vendorinvitation',
            name='max_attempts',
            field=models.IntegerField(default=3),
        ),
        migrations.AddField(
            model_name='vendorprofile',
            name='verification_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vendorprofile',
            name='verification_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('verified', 'Verified'), ('rejected', 'Rejected')], default='pending', max_length=10),
        ),
    ]
