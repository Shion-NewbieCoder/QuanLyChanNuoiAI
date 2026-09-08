from rest_framework import serializers

from apps.herds.models import Herd


class ReminderRequestSerializer(serializers.Serializer):
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


class HerdSummaryRequestSerializer(serializers.Serializer):
    herd_id = serializers.IntegerField()

    def validate_herd_id(self, value):
        if not Herd.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Herd does not exist.")
        return value


class GrowthReportRequestSerializer(serializers.Serializer):
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
