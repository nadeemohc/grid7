# Generated by Django 5.0.3 on 2024-05-06 11:37

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('c_id', models.BigAutoField(primary_key=True, serialize=False, unique=True)),
                ('c_name', models.CharField(max_length=50, null=True)),
                ('c_image', models.ImageField(default='category.jpg', upload_to='category')),
                ('is_blocked', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('p_id', models.BigAutoField(primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(default='product', max_length=100)),
                ('description', models.TextField(blank=True, default='This is the product', null=True)),
                ('specifications', models.TextField(blank=True, null=True)),
                ('shipping', models.TextField(null=True)),
                ('availability', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='store.category')),
            ],
            options={
                'verbose_name_plural': 'Products',
            },
        ),
        migrations.CreateModel(
            name='ProductAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, default=1.99, max_digits=10)),
                ('old_price', models.DecimalField(decimal_places=2, default=2.99, max_digits=10)),
                ('stock', models.IntegerField(default=1)),
                ('is_blocked', models.BooleanField(default=False)),
                ('status', models.BooleanField(default=True)),
                ('in_stock', models.BooleanField(default=True)),
                ('featured', models.BooleanField(default=False)),
                ('latest', models.BooleanField(default=False)),
                ('popular', models.BooleanField(default=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('p_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='p_id_attributes', to='store.product')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_attributes', to='store.product')),
                ('related', models.ManyToManyField(blank=True, to='store.productattribute')),
                ('size', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.size')),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveBigIntegerField(default=1)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='store.cart')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.productattribute')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('images', models.ImageField(default='product.jpg', upload_to='product_images')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='store.product')),
            ],
            options={
                'verbose_name_plural': 'Product Images',
            },
        ),
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('sid', models.BigAutoField(primary_key=True, serialize=False, unique=True)),
                ('sub_name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('category', models.ForeignKey(db_column='c_id', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='store.category')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='sub_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='store.subcategory'),
        ),
    ]
