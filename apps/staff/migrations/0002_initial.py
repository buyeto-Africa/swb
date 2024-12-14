# Generated by Django 5.1.4 on 2024-12-13 23:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('staff', '0001_initial'),
        ('userauths', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffinvitation',
            name='invited_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='userauths.user'),
        ),
        migrations.AddField(
            model_name='staffprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='staff_profile', to='userauths.user'),
        ),
        migrations.AddField(
            model_name='staffrole',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='userauths.user'),
        ),
        migrations.AddField(
            model_name='staffprofile',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='staffprofile_set', to='staff.staffrole'),
        ),
        migrations.AddField(
            model_name='staffinvitation',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='staff.staffrole'),
        ),
        migrations.AddIndex(
            model_name='staffprofile',
            index=models.Index(fields=['role'], name='staff_staff_role_id_e85e27_idx'),
        ),
        migrations.AddIndex(
            model_name='staffprofile',
            index=models.Index(fields=['is_active'], name='staff_staff_is_acti_a176ab_idx'),
        ),
    ]
