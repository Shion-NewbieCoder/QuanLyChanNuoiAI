from datetime import date

from rest_framework import serializers

from apps.domain_validation import validate_vaccine_schedule

from .models import VaccinationRecord, VaccineSchedule


def get_alert_classification(schedule, today=None):
    if schedule.status in {VaccineSchedule.Status.COMPLETED, VaccineSchedule.Status.CANCELLED}:
        return None

    today = today or date.today()
    delta = (schedule.scheduled_date - today).days

    if delta < 0:
        return "overdue"
    if delta == 0:
        return "due today"
    if delta <= 7:
        return "due soon"
    return "scheduled-not-yet-due"


class VaccineScheduleSerializer(serializers.ModelSerializer):
    alert_classification = serializers.SerializerMethodField()

    class Meta:
        model = VaccineSchedule
        fields = [
            "id",
            "target",
            "vaccine",
            "scheduled_date",
            "status",
            "alert_classification",
        ]

    def get_alert_classification(self, obj):
        return get_alert_classification(obj)

    def validate_status(self, value):
        valid_statuses = {choice[0] for choice in VaccineSchedule.Status.choices}
        if value not in valid_statuses:
            raise serializers.ValidationError(
                "status must be one of: scheduled, due, completed, cancelled."
            )
        return value

    def validate(self, attrs):
        instance = self.instance or VaccineSchedule()
        for field_name in ["target", "vaccine", "scheduled_date", "status"]:
            if field_name in attrs:
                setattr(instance, field_name, attrs[field_name])
        validate_vaccine_schedule(instance)
        return attrs


class VaccinationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccinationRecord
        fields = ["id", "schedule", "actual_date", "notes"]

    def validate(self, attrs):
        instance = self.instance or VaccinationRecord()
        for field_name in ["schedule", "actual_date", "notes"]:
            if field_name in attrs:
                setattr(instance, field_name, attrs[field_name])

        if instance.schedule_id is None:
            raise serializers.ValidationError({"schedule": "schedule is required."})
        if instance.actual_date is None:
            raise serializers.ValidationError({"actual_date": "actual_date is required."})
        if instance.schedule_id is not None and not VaccineSchedule.objects.filter(pk=instance.schedule_id).exists():
            raise serializers.ValidationError({"schedule": "Invalid schedule reference."})
        return attrs
