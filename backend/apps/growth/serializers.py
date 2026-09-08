from decimal import Decimal

from rest_framework import serializers

from apps.domain_validation import validate_growth_record

from .models import GrowthRecord


class GrowthRecordSerializer(serializers.ModelSerializer):
    weight = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0"))

    class Meta:
        model = GrowthRecord
        fields = ["id", "target", "measurement_date", "weight", "notes"]

    def validate(self, attrs):
        instance = self.instance or GrowthRecord()
        for field_name in ["target", "measurement_date", "weight", "notes"]:
            if field_name in attrs:
                setattr(instance, field_name, attrs[field_name])
        validate_growth_record(instance)
        return attrs
