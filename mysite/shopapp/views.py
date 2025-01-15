from timeit import default_timer
import logging
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.auth.models import Group, User
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from .common import save_csv_products
from .models import Product, Order, ProductImage
from .forms import GroupForm, ProductForm
from rest_framework.viewsets import ModelViewSet
from .serializers import ProductSerializer, OrderSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import action
from csv import DictWriter

log = logging.getLogger(__name__)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        "delivery_address",
        "promocode",
        "created_at",
        "products",
        "user",
    ]
    search_fields = [
        "delivery_address",
        "products",
        "user",
    ]
    ordering_fields = [
        "delivery_address",
        "products",
        "user",
    ]


@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product.
    Полный CRUD для сущностей товара.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ["name", "description", "price", "discount", "archived"]
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, returns 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by ID not found"),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = ["name", "description", "price", "discount"]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for product in queryset:
            writer.writerow({field: getattr(product, field) for field in fields})
        return response

    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser])
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"].file, encoding=request.encoding
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class ShopIndexView(View):
    # @method_decorator(cache_page(60 * 2))
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ("Laptop", 1999),
            ("Desktop", 2999),
            ("Smartphone", 999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
            "items": 5,
        }
        print("shop index context", context)
        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index")
        return render(request, "shopapp/shop-index.html", context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related("permissions").all(),
        }
        return render(request, "shopapp/groups-list.html", context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = "shopapp/products-details.html"
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductListView(ListView):
    template_name = "shopapp/products-list.html"
    model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


# @method_decorator(
#     permission_required("add_product", raise_exception=True), name="dispatch"
# )
class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "add_product"
    model = Product
    fields = "name", "price", "description", "discount", "preview"
    success_url = reverse_lazy("shopapp:products_list")

    # def test_func(self):
    #     self.request.user.groups.filter(name='secret-group').exists()
    #     return self.request.user.is_superuser

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.created_by = self.request.user
        return response


@method_decorator(
    permission_required("change_product", raise_exception=True), name="dispatch"
)
class ProductUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        if self.request.user == Product.created_by or self.request.user.is_superuser:
            return True

    model = Product
    # fields = "name", "price", "description", "discount", "preview"
    template_name_suffix = "_update_form"
    form_class = ProductForm

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrderCreateView(CreateView):
    model = Order
    fields = "user", "products", "delivery_address", "promocode"
    success_url = reverse_lazy("shopapp:orders_list")


class OrderListView(LoginRequiredMixin, ListView):
    template_name = "shopapp/orders_list.html"
    queryset = Order.objects.select_related("user").prefetch_related("products")


class OrdersDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    template_name = "shopapp/order_details.html"
    queryset = Order.objects.select_related("user").prefetch_related("products")


class UserOrdersListView(LoginRequiredMixin, ListView):
    template_name = "shopapp/user_orders.html"

    def get_object(self):
        pk = self.kwargs["user_id"]
        self.owner = get_object_or_404(User, id=pk)
        return self.owner

    def get_queryset(self):
        self.get_object()
        return (
            Order.objects.select_related("user")
            .filter(user=self.owner)
            .prefetch_related("products")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["owner"] = self.owner
        context["orders"] = self.queryset
        return context


class OrderUpdateView(UpdateView):
    model = Order
    fields = "delivery_address", "promocode", "user", "products"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk},
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:orders_list")


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,
                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)
        return JsonResponse({"products": products_data})


class OrdersDataExportView(UserPassesTestMixin, View):
    def test_func(self):
        if self.request.user.is_staff:
            return True

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by("pk").all()
        orders_data = [
            {
                "id": order.id,
                "address": order.delivery_address,
                "promocode": order.promocode,
                "user": order.user,
                "products": order.products,
            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})


class UserOrdersExportView(View):

    def get_object(self):
        pk = self.kwargs["user_id"]
        self.owner = get_object_or_404(User, id=pk)
        return self.owner

    def get(self, request: HttpRequest) -> JsonResponse:
        self.get_object()
        cache_key = "orders_data_export"
        orders_data = cache.get(cache_key)
        if orders_data is None:
            orders = (
                Order.objects.select_related("user")
                .filter(user=self.owner)
                .order_by("pk")
                .prefetch_related("products")
            )
            orders_data = [
                {
                    "id": order.id,
                    "address": order.delivery_address,
                    "promocode": order.promocode,
                    "user": order.user,
                    "products": order.products,
                }
                for order in orders
            ]
            cache.set(cache_key, orders_data, 300)
        return JsonResponse({"orders": orders_data})


class LatestProductsFeed(Feed):
    title = "Products(latest)"
    description = "Updates on changes and addition products"
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        return Product.objects.all().order_by("-price")[:5]

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:100]
