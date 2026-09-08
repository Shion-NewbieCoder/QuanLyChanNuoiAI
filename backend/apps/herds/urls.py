from rest_framework.routers import DefaultRouter

from .views import AnimalGroupViewSet, AnimalViewSet, HerdViewSet

router = DefaultRouter()
router.register(r"herds", HerdViewSet, basename="herd")
router.register(r"animals", AnimalViewSet, basename="animal")
router.register(r"animal-groups", AnimalGroupViewSet, basename="animalgroup")

urlpatterns = router.urls
