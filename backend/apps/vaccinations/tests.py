from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.herds.models import Herd

from .models import VaccinationRecord, VaccineSchedule


class VaccineScheduleModelTests(TestCase):
    def setUp(self):
        self.herd = Herd.objects.create(
            code="HERD-100",
            name="Đàn bò",
            animal_type="bò",
            management_mode="group",
            quantity=20,
            status="active",
        )

    def test_schedule_001_valid_schedule(self):
        schedule = VaccineSchedule(
            target=self.herd,
            vaccine="Vắc xin viêm da",
            scheduled_date=date(2026, 9, 15),
            status=VaccineSchedule.Status.SCHEDULED,
        )

        schedule.full_clean()
        schedule.save()
        self.assertEqual(VaccineSchedule.objects.get(pk=schedule.pk).target_id, self.herd.pk)

    def test_schedule_002_missing_required_vaccine_fails(self):
        schedule = VaccineSchedule(
            target=self.herd,
            vaccine="",
            scheduled_date=date(2026, 9, 15),
            status=VaccineSchedule.Status.SCHEDULED,
        )

        with self.assertRaises(ValidationError):
            schedule.full_clean()

    def test_schedule_003_missing_required_scheduled_date_fails(self):
        schedule = VaccineSchedule(
            target=self.herd,
            vaccine="Vắc xin viêm da",
            scheduled_date=None,
            status=VaccineSchedule.Status.SCHEDULED,
        )

        with self.assertRaises(ValidationError):
            schedule.full_clean()

    def test_schedule_004_invalid_herd_reference_fails(self):
        schedule = VaccineSchedule(
            target_id=999999,
            vaccine="Vắc xin viêm da",
            scheduled_date=date(2026, 9, 15),
            status=VaccineSchedule.Status.SCHEDULED,
        )

        with self.assertRaises(ValidationError):
            schedule.full_clean()

    def test_schedule_005_status_values_are_valid(self):
        for status_value in [
            VaccineSchedule.Status.SCHEDULED,
            VaccineSchedule.Status.DUE,
            VaccineSchedule.Status.COMPLETED,
            VaccineSchedule.Status.CANCELLED,
        ]:
            schedule = VaccineSchedule(
                target=self.herd,
                vaccine="Vắc xin viêm da",
                scheduled_date=date(2026, 9, 15),
                status=status_value,
            )
            schedule.full_clean()

    def test_schedule_006_persistence(self):
        schedule = VaccineSchedule.objects.create(
            target=self.herd,
            vaccine="Vắc xin viêm da",
            scheduled_date=date(2026, 9, 15),
            status=VaccineSchedule.Status.DUE,
        )
        loaded = VaccineSchedule.objects.get(pk=schedule.pk)

        self.assertEqual(loaded.target_id, self.herd.pk)
        self.assertEqual(loaded.vaccine, schedule.vaccine)
        self.assertEqual(loaded.scheduled_date, schedule.scheduled_date)
        self.assertEqual(loaded.status, schedule.status)


class VaccinationRecordModelTests(TestCase):
    def setUp(self):
        self.herd = Herd.objects.create(
            code="HERD-200",
            name="Đàn lợn",
            animal_type="lợn",
            management_mode="group",
            quantity=30,
            status="active",
        )
        self.schedule = VaccineSchedule.objects.create(
            target=self.herd,
            vaccine="Vắc xin tụ huyết trùng",
            scheduled_date=date(2026, 9, 20),
            status=VaccineSchedule.Status.SCHEDULED,
        )

    def test_record_001_valid_record(self):
        record = VaccinationRecord(
            schedule=self.schedule,
            actual_date=date(2026, 9, 20),
            notes="Tiêm đúng lịch",
        )

        record.full_clean()
        record.save()
        self.assertEqual(VaccinationRecord.objects.get(pk=record.pk).schedule_id, self.schedule.pk)

    def test_record_002_optional_notes_allowed(self):
        record = VaccinationRecord(
            schedule=self.schedule,
            actual_date=date(2026, 9, 20),
        )

        record.full_clean()
        record.save()
        self.assertEqual(record.notes, "")

    def test_record_003_missing_actual_date_fails(self):
        record = VaccinationRecord(
            schedule=self.schedule,
            actual_date=None,
            notes="Tiêm đúng lịch",
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_record_004_invalid_schedule_reference_fails(self):
        record = VaccinationRecord(
            schedule_id=999999,
            actual_date=date(2026, 9, 20),
            notes="Tiêm đúng lịch",
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_record_005_persistence(self):
        record = VaccinationRecord.objects.create(
            schedule=self.schedule,
            actual_date=date(2026, 9, 20),
            notes="Tiêm xong",
        )
        loaded = VaccinationRecord.objects.get(pk=record.pk)

        self.assertEqual(loaded.schedule_id, self.schedule.pk)
        self.assertEqual(loaded.actual_date, record.actual_date)
        self.assertEqual(loaded.notes, record.notes)
