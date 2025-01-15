from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse
from string import ascii_letters
from random import choices
from django.conf import settings
from shopapp.models import Product, Order
from shopapp.utils import add_two_numbers


class AddTwoNumbers(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


class ProductCreateViewTestCase(TestCase):
    def setUp(self) -> None:
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(
            reverse("shopapp:product_create"),
            {
                "name": self.product_name,
                "price": "123.45",
                "description": "a good table",
                "discount": "10",
            },
        )
        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(Product.objects.filter(name=self.product_name).exists())


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create(username="testuser")
        cls.product = Product.objects.create(name="Best product", created_by=cls.user)

    # def setUp(self) -> None:
    #     self.user = User.objects.create(username="testuser")
    #     self.product = Product.objects.create(name="Best product", created_by=self.user)

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    # def tearDown(self) -> None:
    #     self.product.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        "products-fixture.json",
    ]

    def test_products(self):
        response = self.client.get(reverse("shopapp:products_list"))
        # products = Product.objects.filter(archived=False).all()
        # products_context = response.context["products"]
        # for p, p_ in zip(products, products_context):
        #     self.assertEqual(p.pk, p_.pk)
        self.assertQuerySetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context["products"]),
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, "shopapp/products-list.html")

        # for product in Product.objects.filter(archived=False).all():
        #     self.assertContains(response, product.name)


class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="bob", password="qwerty")
        # cls.credentials = dict(username="bob", password="qwerty")
        # cls.user = User.objects.create_user(**cls.credentials)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        # self.client.login(**self.credentials)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertContains(response, "Orders")

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductExportViewTestCase(TestCase):
    fixtures = [
        "products-fixture.json",
    ]

    def test_get_products_view(self):
        response = self.client.get(
            reverse("shopapp:products-export"),
        )
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(products_data["products"], expected_data)


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="john", password="qwerty")
        permission = Permission.objects.get(codename="view_order")
        cls.user.user_permissions.add(permission)

    def setUp(self):
        self.client.force_login(self.user)
        self.order = Order.objects.create(user=self.user)
        self.assertTrue(Order.objects.filter(id=self.order.id).exists())

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_order_details(self):
        response = self.client.get(
            reverse("shopapp:order_details", kwargs={"pk": self.order.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.client.logout()


class OrderExportTestCase(TestCase):
    fixtures = [
        "orders-fixture.json",
    ]

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="bill", password="qwerty")
        cls.user.is_staff = True
        cls.user.save()

    def setUp(self):
        self.client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_get_order_list(self):
        response = self.client.get(
            reverse("shopapp:orders-export"),
        )
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by("pk").all()
        expected_data = [
            {
                "id": order.id,
                "address": order.delivery_address,
                "promocode": order.promocode,
                "user": order.user,
                "products": order.products,
            }
            for order in orders
        ]
        orders_data = response.json()
        self.assertEqual(orders_data["orders"], expected_data)
