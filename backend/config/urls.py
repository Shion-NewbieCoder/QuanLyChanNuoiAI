"""URL configuration for authentication and the protected test surface."""

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

from apps.users.views import protected_operation


urlpatterns = [
    path("", include("apps.dashboard.urls")),
    path("api/ai/", include("apps.ai.urls")),
    path(
        "login/",
        LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("auth/protected/", protected_operation, name="protected-operation"),
    path("api/", include("apps.herds.urls")),
    path("api/", include("apps.pens.urls")),
    path("api/", include("apps.care.urls")),
    path("api/", include("apps.vaccinations.urls")),
    path("api/", include("apps.growth.urls")),
    path("api/", include("apps.reproduction.urls")),
    path("api/", include("apps.sales.urls")),
    path("api/", include("apps.statistics.urls")),
]
