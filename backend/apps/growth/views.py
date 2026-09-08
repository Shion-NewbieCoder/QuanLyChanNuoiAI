from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import RoleActionPermission
from config.filters import ExactFieldFilterBackend

from .models import GrowthRecord
from .serializers import GrowthRecordSerializer


class GrowthRecordViewSet(viewsets.ModelViewSet):
    queryset = GrowthRecord.objects.all()
    serializer_class = GrowthRecordSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "growth_reproduction"
    filter_backends = [filters.SearchFilter, ExactFieldFilterBackend, filters.OrderingFilter]
    search_fields = ["notes"]
    exact_filter_fields = ["target"]
    ordering_fields = ["measurement_date", "weight"]
