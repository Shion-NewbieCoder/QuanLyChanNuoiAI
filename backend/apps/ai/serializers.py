from collections.abc import Mapping

from rest_framework import serializers

from apps.herds.models import Herd


class AIRequestSerializer(serializers.Serializer):
    """Only application-defined selection fields; never accept client instructions."""

    def to_internal_value(self, data):
        if isinstance(data, Mapping) and set(data) - set(self.fields):
            raise serializers.ValidationError({"non_field_errors": ["Unsupported AI request fields."]})
        return super().to_internal_value(data)


class ReminderRequestSerializer(AIRequestSerializer):
    scope = serializers.ChoiceField(choices=["all", "herd"])
    target_id = serializers.IntegerField(required=False, allow_null=True)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    def validate(self, attrs):
        scope = attrs["scope"]
        target_id = attrs.get("target_id")
        if scope == "herd" and target_id is None:
            raise serializers.ValidationError({"target_id": "This field is required for herd scope."})
        if scope == "all" and target_id is not None:
            raise serializers.ValidationError({"target_id": "Must be omitted or null for all scope."})
        if target_id is not None and not Herd.objects.filter(pk=target_id).exists():
            raise serializers.ValidationError({"target_id": "Herd does not exist."})
        if attrs.get("start_date") and attrs.get("end_date") and attrs["start_date"] > attrs["end_date"]:
            raise serializers.ValidationError({"end_date": "Must be on or after start_date."})
        return attrs


class HerdSummaryRequestSerializer(AIRequestSerializer):
    herd_id = serializers.IntegerField()

    def validate_herd_id(self, value):
        if not Herd.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Herd does not exist.")
        return value


class GrowthReportRequestSerializer(AIRequestSerializer):
    herd_id = serializers.IntegerField()
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    def validate_herd_id(self, value):
        if not Herd.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Herd does not exist.")
        return value

    def validate(self, attrs):
        if attrs.get("start_date") and attrs.get("end_date") and attrs["start_date"] > attrs["end_date"]:
            raise serializers.ValidationError({"end_date": "Must be on or after start_date."})
        return attrs


class ChatRequestSerializer(AIRequestSerializer):
    question = serializers.CharField(max_length=500, trim_whitespace=True)
