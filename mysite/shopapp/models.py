from fileinput import filename

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def product_preview_directory_path(instanse: "Product", filename: str) -> str:
    return "products/product_{pk}/preview/{filename}".format(
        pk=instanse.pk,
        filename=filename,
    )


def get_deleted_user():
    return User.objects.get_or_create(username="deleted_user")[0]


class Product(models.Model):
    """
    Модель Product представляет товар, который можно продавать в интернет магазине.

    Заказы тут: :model:`shopapp. Order`
    """

    class Meta:
        ordering = ["name", "price"]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, default=get_deleted_user, null=True
    )
    archived = models.BooleanField(default=False)
    preview = models.ImageField(
        null=True, blank=True, upload_to=product_preview_directory_path
    )

    def get_absolute_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.pk})

    def __str__(self):
        return f"Product(pk={self.pk}, name={self.name!r})"


def product_images_directory_path(instanse: "ProductImage", filename: str) -> str:
    return "products/product_{pk}/images/{filename}".format(
        pk=instanse.product.pk,
        filename=filename,
    )


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to=product_images_directory_path)
    description = models.CharField(max_length=200, null=False, blank=True)


class Order(models.Model):
    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    delivery_address = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name="orders")
    receipt = models.FileField(null=True, upload_to="orders/receipts/")
