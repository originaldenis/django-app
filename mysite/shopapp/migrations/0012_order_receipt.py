# Generated by Django 5.1 on 2024-10-22 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shopapp", "0011_alter_product_created_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="receipt",
            field=models.FileField(null=True, upload_to="orders/receipts/"),
        ),
    ]
