from rest_framework.routers import DefaultRouter

from .views import CareLogViewSet, FeedRecordViewSet, MedicineRecordViewSet

router = DefaultRouter()
router.register(r"care-logs", CareLogViewSet, basename="carelog")
router.register(r"feed-records", FeedRecordViewSet, basename="feedrecord")
router.register(r"medicine-records", MedicineRecordViewSet, basename="medicinerecord")

urlpatterns = router.urls
