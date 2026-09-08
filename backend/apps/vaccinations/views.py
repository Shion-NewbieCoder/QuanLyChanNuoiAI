from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import RoleActionPermission
from config.filters import ExactFieldFilterBackend

from .models import VaccinationRecord, VaccineSchedule
from .serializers import VaccineScheduleSerializer, VaccinationRecordSerializer


class VaccineScheduleViewSet(viewsets.ModelViewSet):
    queryset = VaccineSchedule.objects.all()
    serializer_class = VaccineScheduleSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "vaccination"
    filter_backends = [filters.SearchFilter, ExactFieldFilterBackend, filters.OrderingFilter]
    search_fields = ["vaccine"]
    exact_filter_fields = ["target", "status"]
    ordering_fields = ["scheduled_date", "vaccine"]


class VaccinationRecordViewSet(viewsets.ModelViewSet):
    queryset = VaccinationRecord.objects.all()
    serializer_class = VaccinationRecordSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "vaccination"
    filter_backends = [filters.SearchFilter, ExactFieldFilterBackend, filters.OrderingFilter]
    search_fields = ["notes"]
    exact_filter_fields = ["schedule"]
    ordering_fields = ["actual_date"]
