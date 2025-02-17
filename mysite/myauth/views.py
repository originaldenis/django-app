from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages import success
from django.http import (
    HttpRequest,
    HttpResponse,
    JsonResponse,
    HttpResponseRedirect,
    request,
)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LogoutView
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (
    TemplateView,
    CreateView,
    UpdateView,
    ListView,
    DetailView,
)
from django.utils.translation import gettext_lazy as _, ngettext
from .models import Profile
from random import random


class HelloView(View):
    welcome_message = _("welcome hello world!")

    def get(self, request: HttpRequest) -> HttpResponse:
        items_string = request.GET.get("items") or 0
        items = int(items_string)
        products_line = ngettext(
            "one product",
            "{count} products",
            items,
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>" f"<h2>{products_line}</h2>"
        )


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(self.request, username=username, password=password)
        login(request=self.request, user=user)
        return response


class AboutMeView(LoginRequiredMixin, UpdateView):
    def get_object(self, queryset=None):
        if not Profile.objects.filter(user=self.request.user).exists():
            Profile.objects.get_or_create(user=self.request.user)
        return self.request.user.profile

    model = Profile
    template_name = "myauth/about-me.html"
    fields = ("avatar",)
    success_url = reverse_lazy("myauth:about-me", context={"user": get_object})


class UsersListView(ListView):
    model = User
    template_name = "myauth/users-list.html"
    queryset = User.objects.all()
    context_object_name = "users"


class UsersDetailsView(UpdateView, UserPassesTestMixin):
    def test_func(self):
        if self.request.user.id == self.request.pk or self.request.user.is_staff:
            return True

    def get_object(self, queryset=None):
        pk = self.kwargs["pk"]
        details_user = get_object_or_404(User, id=pk)
        return details_user

    model = Profile
    fields = ("avatar",)
    template_name = "myauth/user-details.html"
    success_url = reverse_lazy("myauth:user-details", context={"user": get_object})


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/admin/")
        return render(request, "myauth/login.html")

    username = request.POST["username"]
    password = request.POST["password"]

    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        return redirect("/admin/")
    return render(request, "myauth/login.html", {"error": "Invalid login credentials"})


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


@cache_page(60 * 2)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value:{value!r} + {random()}")


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", " default")
    return HttpResponse(f"Session value: {value!r}")


# def logout_view(request: HttpRequest):
#     logout(request)
#     return redirect(reverse('myauth:login'))

# class MyLogoutView(LogoutView):
#     next_page = reverse_lazy("myauth:login")


class MyLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("myauth:login")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})
