# Generated by Django 5.1 on 2024-10-22 13:49

import django.db.models.deletion
import shopapp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shopapp", "0013_product_preview"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        upload_to=shopapp.models.product_images_directory_path
                    ),
                ),
                ("description", models.CharField(blank=True, max_length=200)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="shopapp.product",
                    ),
                ),
            ],
        ),
    ]
