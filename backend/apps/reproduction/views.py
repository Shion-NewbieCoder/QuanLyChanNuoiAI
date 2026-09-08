from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import RoleActionPermission
from config.filters import ExactFieldFilterBackend

from .models import ReproductionRecord
from .serializers import ReproductionRecordSerializer


class ReproductionRecordViewSet(viewsets.ModelViewSet):
    queryset = ReproductionRecord.objects.all()
    serializer_class = ReproductionRecordSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "growth_reproduction"
    filter_backends = [filters.SearchFilter, ExactFieldFilterBackend, filters.OrderingFilter]
    search_fields = ["event_type", "result", "notes"]
    exact_filter_fields = ["target"]
    ordering_fields = ["event_date"]
