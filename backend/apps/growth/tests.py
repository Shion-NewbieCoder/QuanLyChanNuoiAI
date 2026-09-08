from datetime import date

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.herds.models import Herd

from .models import GrowthRecord


class GrowthRecordModelTests(TestCase):
    def setUp(self):
        self.herd = Herd.objects.create(
            code="HERD-300",
            name="Đàn bò sữa",
            animal_type="bò",
            management_mode="group",
            quantity=25,
            status="active",
        )

    def test_growth_001_valid_record(self):
        record = GrowthRecord(
            target=self.herd,
            measurement_date=date(2026, 9, 10),
            weight=Decimal("120.50"),
            notes="Cân nặng đầu tháng",
        )

        record.full_clean()
        record.save()
        self.assertEqual(GrowthRecord.objects.get(pk=record.pk).target_id, self.herd.pk)

    def test_growth_002_missing_measurement_date_fails(self):
        record = GrowthRecord(
            target=self.herd,
            measurement_date=None,
            weight=Decimal("120.50"),
            notes="Cân nặng đầu tháng",
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_growth_003_missing_weight_fails(self):
        record = GrowthRecord(
            target=self.herd,
            measurement_date=date(2026, 9, 10),
            weight=None,
            notes="Cân nặng đầu tháng",
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_growth_004_negative_weight_fails(self):
        record = GrowthRecord(
            target=self.herd,
            measurement_date=date(2026, 9, 10),
            weight=Decimal("-1.00"),
            notes="Cân nặng âm",
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_growth_005_missing_target_fails(self):
        record = GrowthRecord(
            target_id=999999,
            measurement_date=date(2026, 9, 10),
            weight=Decimal("120.50"),
            notes="Cân nặng đầu tháng",
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_growth_006_optional_notes_allowed(self):
        record = GrowthRecord(
            target=self.herd,
            measurement_date=date(2026, 9, 10),
            weight=Decimal("120.50"),
        )

        record.full_clean()
        record.save()
        self.assertEqual(record.notes, "")
