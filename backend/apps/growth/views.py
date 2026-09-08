from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import RoleActionPermission

from .models import GrowthRecord
from .serializers import GrowthRecordSerializer


class GrowthRecordViewSet(viewsets.ModelViewSet):
    queryset = GrowthRecord.objects.all()
    serializer_class = GrowthRecordSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "growth_reproduction"
