from datetime import datetime, timezone
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.herds.models import Herd

from .models import CareLog, FeedRecord, MedicineRecord


class CareRecordModelTests(TestCase):
    def setUp(self):
        self.herd = Herd.objects.create(
            code="HERD-001",
            name="Đàn bò sữa",
            animal_type="bò",
            management_mode="group",
            quantity=10,
            status="active",
        )
        self.recorded_at = datetime(2026, 9, 7, 8, 30, tzinfo=timezone.utc)

    def test_care_001_valid_care_log(self):
        record = CareLog(
            herd=self.herd,
            recorded_at=self.recorded_at,
            activity="Vệ sinh chuồng",
        )

        record.full_clean()
        record.save()
        self.assertEqual(CareLog.objects.get(pk=record.pk).herd_id, self.herd.pk)

    def test_care_002_missing_required_field_fails(self):
        record = CareLog(herd=self.herd, recorded_at=self.recorded_at, activity="")

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_care_003_missing_herd_fails(self):
        record = CareLog(
            herd_id=999999,
            recorded_at=self.recorded_at,
            activity="Vệ sinh chuồng",
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_care_004_persistence(self):
        record = CareLog.objects.create(
            herd=self.herd,
            recorded_at=self.recorded_at,
            activity="Vệ sinh chuồng",
            notes="Hoàn thành",
        )
        loaded = CareLog.objects.get(pk=record.pk)

        self.assertEqual(loaded.herd_id, self.herd.pk)
        self.assertEqual(loaded.activity, record.activity)
        self.assertEqual(loaded.notes, record.notes)

    def test_feed_001_valid_feed_record(self):
        record = FeedRecord(
            herd=self.herd,
            recorded_at=self.recorded_at,
            feed_type="Cỏ tươi",
            quantity=Decimal("12.50"),
        )

        record.full_clean()
        record.save()
        self.assertEqual(FeedRecord.objects.get(pk=record.pk).quantity, Decimal("12.50"))

    def test_feed_002_missing_required_field_fails(self):
        record = FeedRecord(
            herd=self.herd,
            recorded_at=self.recorded_at,
            feed_type="",
            quantity=Decimal("1.00"),
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_feed_003_negative_quantity_fails(self):
        record = FeedRecord(
            herd=self.herd,
            recorded_at=self.recorded_at,
            feed_type="Cỏ tươi",
            quantity=Decimal("-1.00"),
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_feed_004_missing_herd_fails(self):
        record = FeedRecord(
            herd_id=999999,
            recorded_at=self.recorded_at,
            feed_type="Cỏ tươi",
            quantity=Decimal("1.00"),
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_feed_005_persistence(self):
        record = FeedRecord.objects.create(
            herd=self.herd,
            recorded_at=self.recorded_at,
            feed_type="Cỏ tươi",
            quantity=Decimal("12.50"),
            notes="Buổi sáng",
        )
        loaded = FeedRecord.objects.get(pk=record.pk)

        self.assertEqual(loaded.herd_id, self.herd.pk)
        self.assertEqual(loaded.feed_type, record.feed_type)
        self.assertEqual(loaded.quantity, record.quantity)
        self.assertEqual(loaded.notes, record.notes)

    def test_med_001_valid_medicine_record(self):
        record = MedicineRecord(
            herd=self.herd,
            recorded_at=self.recorded_at,
            medicine="Vitamin",
            dose=Decimal("2.50"),
        )

        record.full_clean()
        record.save()
        self.assertEqual(MedicineRecord.objects.get(pk=record.pk).dose, Decimal("2.50"))

    def test_med_002_missing_required_field_fails(self):
        record = MedicineRecord(
            herd=self.herd,
            recorded_at=self.recorded_at,
            medicine="",
            dose=Decimal("2.50"),
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_med_003_negative_dose_fails(self):
        record = MedicineRecord(
            herd=self.herd,
            recorded_at=self.recorded_at,
            medicine="Vitamin",
            dose=Decimal("-1.00"),
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_med_004_missing_herd_fails(self):
        record = MedicineRecord(
            herd_id=999999,
            recorded_at=self.recorded_at,
            medicine="Vitamin",
            dose=Decimal("2.50"),
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_med_005_persistence(self):
        record = MedicineRecord.objects.create(
            herd=self.herd,
            recorded_at=self.recorded_at,
            medicine="Vitamin",
            dose=Decimal("2.50"),
            notes="Theo dõi phản ứng",
        )
        loaded = MedicineRecord.objects.get(pk=record.pk)

        self.assertEqual(loaded.herd_id, self.herd.pk)
        self.assertEqual(loaded.medicine, record.medicine)
        self.assertEqual(loaded.dose, record.dose)
        self.assertEqual(loaded.notes, record.notes)
