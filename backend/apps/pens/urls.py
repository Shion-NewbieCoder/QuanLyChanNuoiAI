from rest_framework.routers import DefaultRouter

from .views import PenViewSet

router = DefaultRouter()
router.register(r"pens", PenViewSet, basename="pen")

urlpatterns = router.urls
