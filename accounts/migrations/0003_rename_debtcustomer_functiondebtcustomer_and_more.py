# Generated by Django 5.1.2 on 2024-11-07 05:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_rename_order_id_payment_function_order_id_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DebtCustomer',
            new_name='FunctionDebtCustomer',
        ),
        migrations.DeleteModel(
            name='SalesReport',
        ),
    ]