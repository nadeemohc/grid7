# Generated by Django 5.0.3 on 2024-08-28 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0015_cartorder_wallet_balance_used'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartorder',
            name='discounts',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
