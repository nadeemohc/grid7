# Generated by Django 5.0.3 on 2024-04-20 08:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0031_rename_size_product_size_alter_size_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='product',
        ),
        migrations.DeleteModel(
            name='Cart',
        ),
        migrations.DeleteModel(
            name='CartItem',
        ),
    ]
