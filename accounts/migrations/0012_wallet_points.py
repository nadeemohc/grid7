# Generated by Django 5.0.3 on 2024-07-19 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_alter_wallet_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallet',
            name='points',
            field=models.IntegerField(default=0),
        ),
    ]
