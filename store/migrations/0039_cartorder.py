# Generated by Django 5.0.3 on 2024-04-22 11:33

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_delete_payments'),
        ('store', '0038_payments'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CartOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(default=None, max_length=20)),
                ('order_total', models.FloatField(blank=True, null=True)),
                ('status', models.CharField(choices=[('New', 'New'), ('Paid', 'Paid'), ('Shipped', 'Shipped'), ('Conformed', 'Conformed'), ('Pending', 'Pending'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Return', 'Return')], default='New', max_length=10)),
                ('ip', models.CharField(blank=True, max_length=20)),
                ('is_ordered', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.payments')),
                ('selected_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.address')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Cart Order',
            },
        ),
    ]
