from rest_framework.routers import DefaultRouter

from .views import ReproductionRecordViewSet

router = DefaultRouter()
router.register(r"reproduction-records", ReproductionRecordViewSet, basename="reproductionrecord")

urlpatterns = router.urls
