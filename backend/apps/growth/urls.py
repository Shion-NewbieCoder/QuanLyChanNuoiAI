from rest_framework.routers import DefaultRouter

from .views import GrowthRecordViewSet

router = DefaultRouter()
router.register(r"growth-records", GrowthRecordViewSet, basename="growthrecord")

urlpatterns = router.urls
