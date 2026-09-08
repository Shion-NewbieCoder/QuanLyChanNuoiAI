from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.herds.models import Herd

from .models import SaleRecord


class SaleRecordModelTests(TestCase):
    def setUp(self):
        self.herd = Herd.objects.create(
            code="HERD-500",
            name="Đàn bò thịt",
            animal_type="bò",
            management_mode="group",
            quantity=20,
            status="active",
        )

    def test_sale_001_valid_record(self):
        record = SaleRecord(
            target=self.herd,
            sale_date=date(2026, 9, 15),
            quantity=Decimal("12.00"),
            weight=Decimal("540.50"),
            amount=Decimal("2400.00"),
            notes="Bán 12 con bò",
        )

        record.full_clean()
        record.save()
        self.assertEqual(SaleRecord.objects.get(pk=record.pk).target_id, self.herd.pk)

    def test_sale_002_missing_sale_date_fails(self):
        record = SaleRecord(
            target=self.herd,
            sale_date=None,
            quantity=Decimal("12.00"),
            weight=Decimal("540.50"),
            amount=Decimal("2400.00"),
            notes="Thiếu ngày bán",
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_sale_003_missing_amount_fails(self):
        record = SaleRecord(
            target=self.herd,
            sale_date=date(2026, 9, 15),
            quantity=Decimal("12.00"),
            weight=Decimal("540.50"),
            amount=None,
            notes="Thiếu số tiền",
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_sale_004_missing_target_fails(self):
        record = SaleRecord(
            target_id=999999,
            sale_date=date(2026, 9, 15),
            quantity=Decimal("12.00"),
            weight=Decimal("540.50"),
            amount=Decimal("2400.00"),
            notes="Không có đàn",
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_sale_005_optional_quantity_allowed(self):
        record = SaleRecord(
            target=self.herd,
            sale_date=date(2026, 9, 15),
            weight=Decimal("540.50"),
            amount=Decimal("2400.00"),
        )

        record.full_clean()
        record.save()
        self.assertIsNone(record.quantity)

    def test_sale_006_optional_weight_allowed(self):
        record = SaleRecord(
            target=self.herd,
            sale_date=date(2026, 9, 15),
            quantity=Decimal("12.00"),
            amount=Decimal("2400.00"),
        )

        record.full_clean()
        record.save()
        self.assertIsNone(record.weight)

    def test_sale_007_optional_notes_allowed(self):
        record = SaleRecord(
            target=self.herd,
            sale_date=date(2026, 9, 15),
            quantity=Decimal("12.00"),
            amount=Decimal("2400.00"),
        )

        record.full_clean()
        record.save()
        self.assertEqual(record.notes, "")

    def test_sale_008_negative_amount_fails(self):
        record = SaleRecord(
            target=self.herd,
            sale_date=date(2026, 9, 15),
            quantity=Decimal("12.00"),
            weight=Decimal("540.50"),
            amount=Decimal("-1.00"),
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_sale_009_negative_quantity_fails(self):
        record = SaleRecord(
            target=self.herd,
            sale_date=date(2026, 9, 15),
            quantity=Decimal("-1.00"),
            amount=Decimal("2400.00"),
        )

        with self.assertRaises(ValidationError):
            record.full_clean()
