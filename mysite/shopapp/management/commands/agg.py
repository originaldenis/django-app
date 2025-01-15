from typing import Sequence
from django.db import transaction
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db.models import Avg, Max, Min, Count, Sum

from shopapp.models import Order, Product


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Start demo aggregate")
        orders = Order.objects.annotate(
            total=Sum("products__price", default=0), products_count=Count("products")
        )
        for order in orders:
            print(
                f"Order #{order.id}"
                f"with {order.products_count}"
                f"products worth {order.total}"
            )
        # result = Product.objects.aggregate(
        #     Avg("price"), Max("price"), min_price=Min("price"), count=Count("id")
        # )
        # print(result)
        self.stdout.write("Done")
