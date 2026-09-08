from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.herds.models import Herd

from .models import ReproductionRecord


class ReproductionRecordModelTests(TestCase):
    def setUp(self):
        self.herd = Herd.objects.create(
            code="HERD-400",
            name="Đàn lợn nái",
            animal_type="lợn",
            management_mode="group",
            quantity=18,
            status="active",
        )

    def test_reproduction_001_valid_record(self):
        record = ReproductionRecord(
            target=self.herd,
            event_date=date(2026, 9, 12),
            event_type="đẻ",
            result="thành công",
            notes="Lợn nái khỏe mạnh",
        )

        record.full_clean()
        record.save()
        self.assertEqual(ReproductionRecord.objects.get(pk=record.pk).target_id, self.herd.pk)

    def test_reproduction_002_missing_event_date_fails(self):
        record = ReproductionRecord(
            target=self.herd,
            event_date=None,
            event_type="đẻ",
            result="thành công",
            notes="Lợn nái khỏe mạnh",
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_reproduction_003_missing_event_type_fails(self):
        record = ReproductionRecord(
            target=self.herd,
            event_date=date(2026, 9, 12),
            event_type="",
            result="thành công",
            notes="Lợn nái khỏe mạnh",
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_reproduction_004_optional_result_allowed(self):
        record = ReproductionRecord(
            target=self.herd,
            event_date=date(2026, 9, 12),
            event_type="đẻ",
        )

        record.full_clean()
        record.save()
        self.assertEqual(record.result, "")

    def test_reproduction_005_optional_notes_allowed(self):
        record = ReproductionRecord(
            target=self.herd,
            event_date=date(2026, 9, 12),
            event_type="đẻ",
            result="thành công",
        )

        record.full_clean()
        record.save()
        self.assertEqual(record.notes, "")

    def test_reproduction_006_missing_target_fails(self):
        record = ReproductionRecord(
            target_id=999999,
            event_date=date(2026, 9, 12),
            event_type="đẻ",
            result="thành công",
            notes="Lợn nái khỏe mạnh",
        )

        with self.assertRaises(ValidationError):
            record.full_clean()
