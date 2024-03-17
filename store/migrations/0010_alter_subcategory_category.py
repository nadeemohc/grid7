# Generated by Django 5.0.3 on 2024-03-15 08:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_rename_parent_category_subcategory_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subcategory',
            name='category',
            field=models.ForeignKey(db_column='c_id', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='store.category'),
        ),
    ]
