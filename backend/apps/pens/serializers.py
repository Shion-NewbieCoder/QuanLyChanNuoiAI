from rest_framework import serializers

from apps.domain_validation import validate_pen_target

from .models import Pen


class PenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pen
        fields = [
            "id",
            "code",
            "name",
            "location",
            "description",
            "status",
            "herd",
            "animal_group",
            "animal",
        ]

    def validate(self, attrs):
        instance = self.instance or Pen()
        for field_name in [
            "code",
            "name",
            "location",
            "description",
            "status",
            "herd",
            "animal_group",
            "animal",
        ]:
            if field_name in attrs:
                setattr(instance, field_name, attrs[field_name])

        validate_pen_target(instance)
        return attrs
