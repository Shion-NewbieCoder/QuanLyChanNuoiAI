from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import RoleActionPermission

from .models import ReproductionRecord
from .serializers import ReproductionRecordSerializer


class ReproductionRecordViewSet(viewsets.ModelViewSet):
    queryset = ReproductionRecord.objects.all()
    serializer_class = ReproductionRecordSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "growth_reproduction"
