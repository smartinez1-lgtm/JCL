"""Project level URL configuration."""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import TemplateView

from core import views


urlpatterns = [
    path(
        "service-worker.js",
        TemplateView.as_view(template_name="service-worker.js", content_type="application/javascript"),
        name="service_worker",
    ),
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/signup/", views.signup_view, name="signup"),
    path("", include("core.urls")),
]
