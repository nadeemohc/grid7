# Generated by Django 5.0.3 on 2024-03-15 08:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_product_productimages'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subcategory',
            old_name='parent_category',
            new_name='category',
        ),
    ]