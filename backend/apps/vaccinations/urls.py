from rest_framework.routers import DefaultRouter

from .views import VaccinationRecordViewSet, VaccineScheduleViewSet

router = DefaultRouter()
router.register(r"vaccine-schedules", VaccineScheduleViewSet, basename="vaccineschedule")
router.register(r"vaccination-records", VaccinationRecordViewSet, basename="vaccinationrecord")

urlpatterns = router.urls
