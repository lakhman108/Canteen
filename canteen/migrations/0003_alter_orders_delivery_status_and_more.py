# Generated by Django 4.2.11 on 2024-03-29 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canteen', '0002_remove_orderdetails_item_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='delivery_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Delivered', 'Delivered')], default='Pending', max_length=255),
        ),
        migrations.AlterField(
            model_name='orders',
            name='payment_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending', max_length=255),
        ),
    ]