# Generated by Django 5.1.4 on 2024-12-15 23:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0004_alter_passwordreset_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='passwordreset',
            options={'verbose_name': 'Password Reset', 'verbose_name_plural': 'Password Resets'},
        ),
    ]
