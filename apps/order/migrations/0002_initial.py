# Generated by Django 5.1.4 on 2024-12-15 16:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('order', '0001_initial'),
        ('product', '0001_initial'),
        ('userauths', '0003_passwordreset'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='product.product'),
        ),
        migrations.AddField(
            model_name='orderstatushistory',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='userauths.user'),
        ),
        migrations.AddField(
            model_name='orderstatushistory',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_history', to='order.order'),
        ),
    ]
