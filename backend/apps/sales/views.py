from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import RoleActionPermission

from .models import SaleRecord
from .serializers import SaleRecordSerializer


class SaleRecordViewSet(viewsets.ModelViewSet):
    queryset = SaleRecord.objects.all()
    serializer_class = SaleRecordSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "sales"
