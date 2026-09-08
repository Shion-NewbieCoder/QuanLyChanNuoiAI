from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import RoleActionPermission
from config.filters import ExactFieldFilterBackend

from .models import SaleRecord
from .serializers import SaleRecordSerializer


class SaleRecordViewSet(viewsets.ModelViewSet):
    queryset = SaleRecord.objects.all()
    serializer_class = SaleRecordSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "sales"
    filter_backends = [filters.SearchFilter, ExactFieldFilterBackend, filters.OrderingFilter]
    search_fields = ["notes"]
    exact_filter_fields = ["target"]
    ordering_fields = ["sale_date", "amount"]
