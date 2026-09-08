from django.urls import path
from django.views.generic import RedirectView
from . import ui
from .resources import RESOURCES

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="dashboard", permanent=False)),
    path("statistics/", ui.statistics_screen, name="ui-statistics"),
    path("ai/", ui.ai_screen, name="ui-ai"),
]
for slug in RESOURCES:
    for suffix, action in (("", "list"), ("create/", "create"), ("<int:pk>/", "detail"),
                           ("<int:pk>/edit/", "edit"), ("<int:pk>/delete/", "delete")):
        urlpatterns.append(path(f"{slug}/{suffix}", ui.resource_screen,
                                {"slug": slug, "action": action}, name=f"ui-{slug}-{action}"))
