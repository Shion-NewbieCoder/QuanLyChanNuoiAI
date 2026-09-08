from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import RoleActionPermission
from config.filters import ExactFieldFilterBackend

from .models import Animal, AnimalGroup, Herd
from .serializers import AnimalGroupSerializer, AnimalSerializer, HerdSerializer


class HerdViewSet(viewsets.ModelViewSet):
    queryset = Herd.objects.all()
    serializer_class = HerdSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "master_data"
    filter_backends = [filters.SearchFilter, ExactFieldFilterBackend, filters.OrderingFilter]
    search_fields = ["code", "name", "animal_type", "status"]
    exact_filter_fields = ["status", "animal_type", "management_mode"]
    ordering_fields = ["code", "name", "quantity"]


class AnimalViewSet(viewsets.ModelViewSet):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "master_data"
    filter_backends = [filters.SearchFilter, ExactFieldFilterBackend, filters.OrderingFilter]
    search_fields = ["code", "status"]
    exact_filter_fields = ["herd", "status"]
    ordering_fields = ["code"]


class AnimalGroupViewSet(viewsets.ModelViewSet):
    queryset = AnimalGroup.objects.all()
    serializer_class = AnimalGroupSerializer
    permission_classes = [IsAuthenticated, RoleActionPermission]
    permission_resource = "master_data"
    filter_backends = [filters.SearchFilter, ExactFieldFilterBackend, filters.OrderingFilter]
    search_fields = ["code", "name", "status"]
    exact_filter_fields = ["herd", "status"]
    ordering_fields = ["code", "name", "quantity"]
