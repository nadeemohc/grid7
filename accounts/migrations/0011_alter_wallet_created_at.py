# Generated by Django 5.0.3 on 2024-07-19 00:46

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_remove_user_wallet_balance_wallet_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
