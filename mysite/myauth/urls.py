from django.contrib.auth.models import User
from django.urls import path
from .views import (
    login_view,
    get_cookie_view,
    set_cookie_view,
    set_session_view,
    get_session_view,
    MyLogoutView,
    AboutMeView,
    RegisterView,
    FooBarView,
    UsersListView,
    UsersDetailsView,
    HelloView,
)
from django.contrib.auth.views import LoginView

app_name = "myauth"

urlpatterns = [
    # path('login/', login_view, name='login'),
    path(
        "login/",
        LoginView.as_view(
            template_name="myauth/login.html", redirect_authenticated_user=True
        ),
        name="login",
    ),
    path("hello/", HelloView.as_view(), name="hello"),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("cookie/get/", get_cookie_view, name="cookie-get"),
    path("cookie/set/", set_cookie_view, name="cookie-set"),
    path("session/set/", set_session_view, name="session-set"),
    path("session/get/", get_session_view, name="session-get"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("users-list/", UsersListView.as_view(), name="users-list"),
    path("user-details/<int:pk>", UsersDetailsView.as_view(), name="user-details"),
    path("register/", RegisterView.as_view(), name="register"),
    path("foo-bar/", FooBarView.as_view(), name="foo-bar"),
]
