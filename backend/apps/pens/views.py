from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import RoleActionPermission

from .models import Pen
from .serializers import PenSerializer


class PenViewSet(viewsets.ModelViewSet):
    queryset = Pen.objects.all()
    serializer_class = PenSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "master_data"
