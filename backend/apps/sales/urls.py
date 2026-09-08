from rest_framework.routers import DefaultRouter

from .views import SaleRecordViewSet

router = DefaultRouter()
router.register(r"sale-records", SaleRecordViewSet, basename="salerecord")

urlpatterns = router.urls
