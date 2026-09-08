from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import RoleActionPermission

from .models import Animal, AnimalGroup, Herd
from .serializers import AnimalGroupSerializer, AnimalSerializer, HerdSerializer


class HerdViewSet(viewsets.ModelViewSet):
    queryset = Herd.objects.all()
    serializer_class = HerdSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "master_data"


class AnimalViewSet(viewsets.ModelViewSet):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "master_data"


class AnimalGroupViewSet(viewsets.ModelViewSet):
    queryset = AnimalGroup.objects.all()
    serializer_class = AnimalGroupSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "master_data"
