# Generated by Django 5.1.2 on 2024-11-12 10:40

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_alter_orderitems_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
