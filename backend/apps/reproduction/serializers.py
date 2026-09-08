from rest_framework import serializers

from apps.domain_validation import validate_reproduction_record

from .models import ReproductionRecord


class ReproductionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReproductionRecord
        fields = ["id", "target", "event_date", "event_type", "result", "notes"]

    def validate(self, attrs):
        instance = self.instance or ReproductionRecord()
        for field_name in ["target", "event_date", "event_type", "result", "notes"]:
            if field_name in attrs:
                setattr(instance, field_name, attrs[field_name])
        validate_reproduction_record(instance)
        return attrs
