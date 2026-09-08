from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import RoleActionPermission
from config.filters import ExactFieldFilterBackend

from .models import Pen
from .serializers import PenSerializer


class PenViewSet(viewsets.ModelViewSet):
    queryset = Pen.objects.all()
    serializer_class = PenSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "master_data"
    filter_backends = [filters.SearchFilter, ExactFieldFilterBackend, filters.OrderingFilter]
    search_fields = ["code", "name", "location", "description", "status"]
    exact_filter_fields = ["herd", "animal_group", "animal", "status"]
    ordering_fields = ["code", "name"]
