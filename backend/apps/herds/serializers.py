from rest_framework import serializers

from .models import Animal, AnimalGroup, Herd


class HerdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Herd
        fields = [
            "id",
            "code",
            "name",
            "animal_type",
            "management_mode",
            "quantity",
            "status",
        ]

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("quantity must be non-negative.")
        return value


class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ["id", "code", "herd", "status"]


class AnimalGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalGroup
        fields = ["id", "code", "name", "herd", "quantity", "status"]

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("quantity must be non-negative.")
        return value
