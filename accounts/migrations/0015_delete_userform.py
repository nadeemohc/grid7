# Generated by Django 5.0.3 on 2024-07-19 09:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_alter_user_referral_code'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Userform',
        ),
    ]
