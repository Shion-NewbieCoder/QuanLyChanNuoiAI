from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import RoleActionPermission

from .models import VaccinationRecord, VaccineSchedule
from .serializers import VaccineScheduleSerializer, VaccinationRecordSerializer


class VaccineScheduleViewSet(viewsets.ModelViewSet):
    queryset = VaccineSchedule.objects.all()
    serializer_class = VaccineScheduleSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "vaccination"


class VaccinationRecordViewSet(viewsets.ModelViewSet):
    queryset = VaccinationRecord.objects.all()
    serializer_class = VaccinationRecordSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "vaccination"
