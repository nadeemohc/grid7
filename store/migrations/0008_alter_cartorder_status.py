# Generated by Django 5.0.3 on 2024-07-17 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_rename_productt_productorder_product_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartorder',
            name='status',
            field=models.CharField(default='Pending', max_length=20),
        ),
    ]