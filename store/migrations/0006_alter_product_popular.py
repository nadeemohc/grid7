# Generated by Django 5.0.3 on 2024-05-13 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_remove_productattribute_featured_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='popular',
            field=models.BooleanField(default=False),
        ),
    ]