# Generated by Django 5.1.4 on 2024-12-15 16:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0005_customersupportticket_customerwishlist_and_more'),
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerreview',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product'),
        ),
        migrations.AddField(
            model_name='customersupportticket',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='support_tickets', to='customer.customerprofile'),
        ),
        migrations.AddField(
            model_name='customerwishlist',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlists', to='customer.customerprofile'),
        ),
        migrations.AddField(
            model_name='customerwishlist',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product'),
        ),
        migrations.AlterUniqueTogether(
            name='customerreview',
            unique_together={('customer', 'product')},
        ),
        migrations.AlterUniqueTogether(
            name='customerwishlist',
            unique_together={('customer', 'product')},
        ),
    ]
