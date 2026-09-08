from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import RoleActionPermission

from .models import CareLog, FeedRecord, MedicineRecord
from .serializers import CareLogSerializer, FeedRecordSerializer, MedicineRecordSerializer


class CareLogViewSet(viewsets.ModelViewSet):
    queryset = CareLog.objects.all()
    serializer_class = CareLogSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "care"


class FeedRecordViewSet(viewsets.ModelViewSet):
    queryset = FeedRecord.objects.all()
    serializer_class = FeedRecordSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "care"


class MedicineRecordViewSet(viewsets.ModelViewSet):
    queryset = MedicineRecord.objects.all()
    serializer_class = MedicineRecordSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "care"
