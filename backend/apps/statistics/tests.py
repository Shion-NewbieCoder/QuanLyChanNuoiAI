from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.growth.models import GrowthRecord
from apps.herds.models import Herd

from .models import CostRecord, HerdLossRecord
from .services import get_cost_statistics, get_growth_statistics, get_loss_statistics


class StatisticsModelTests(TestCase):
    def setUp(self):
        self.herd = Herd.objects.create(
            code="HERD-STAT-001",
            name="Statistics herd",
            animal_type="cattle",
            management_mode="group",
            quantity=20,
            status="active",
        )

    def valid_loss_data(self, **overrides):
        data = {
            "herd": self.herd,
            "period_start": date(2026, 1, 1),
            "period_end": date(2026, 1, 31),
            "opening_quantity": 20,
            "lost_quantity": 2,
        }
        data.update(overrides)
        return data

    def test_loss_001_valid_record(self):
        record = HerdLossRecord(**self.valid_loss_data())
        record.full_clean()
        record.save()
        self.assertEqual(record.herd_id, self.herd.pk)

    def test_loss_002_opening_quantity_must_be_positive(self):
        with self.assertRaises(ValidationError):
            HerdLossRecord(**self.valid_loss_data(opening_quantity=0)).full_clean()

    def test_loss_003_lost_quantity_must_be_non_negative(self):
        with self.assertRaises(ValidationError):
            HerdLossRecord(**self.valid_loss_data(lost_quantity=-1)).full_clean()

    def test_loss_004_lost_quantity_cannot_exceed_opening_quantity(self):
        with self.assertRaises(ValidationError):
            HerdLossRecord(**self.valid_loss_data(lost_quantity=21)).full_clean()

    def test_loss_005_period_end_must_not_precede_start(self):
        with self.assertRaises(ValidationError):
            HerdLossRecord(
                **self.valid_loss_data(
                    period_start=date(2026, 2, 1),
                    period_end=date(2026, 1, 31),
                )
            ).full_clean()

    def test_cost_006_valid_record(self):
        record = CostRecord(
            herd=self.herd,
            cost_date=date(2026, 1, 10),
            category=CostRecord.Category.FEED,
            amount=Decimal("100.00"),
        )
        record.full_clean()
        record.save()
        self.assertEqual(record.amount, Decimal("100.00"))

    def test_cost_007_invalid_category(self):
        with self.assertRaises(ValidationError):
            CostRecord(
                herd=self.herd,
                cost_date=date(2026, 1, 10),
                category="transport",
                amount=Decimal("100.00"),
            ).full_clean()

    def test_cost_008_negative_amount(self):
        with self.assertRaises(ValidationError):
            CostRecord(
                herd=self.herd,
                cost_date=date(2026, 1, 10),
                category=CostRecord.Category.FEED,
                amount=Decimal("-1.00"),
            ).full_clean()


class StatisticsServiceTests(TestCase):
    def setUp(self):
        self.herd = Herd.objects.create(
            code="HERD-STAT-002",
            name="Statistics herd",
            animal_type="cattle",
            management_mode="group",
            quantity=20,
            status="active",
        )

    def test_growth_009_aggregates_existing_growth_records(self):
        GrowthRecord.objects.create(
            target=self.herd,
            measurement_date=date(2026, 1, 1),
            weight=Decimal("100.00"),
        )
        GrowthRecord.objects.create(
            target=self.herd,
            measurement_date=date(2026, 1, 2),
            weight=Decimal("120.00"),
        )
        self.assertEqual(
            get_growth_statistics(),
            {"record_count": 2, "total_weight": "220.00", "average_weight": "110.00"},
        )

    def test_growth_010_empty_dataset(self):
        self.assertEqual(
            get_growth_statistics(),
            {"record_count": 0, "total_weight": "0.00", "average_weight": None},
        )

    def test_cost_011_total_and_category_aggregation(self):
        CostRecord.objects.create(
            herd=self.herd,
            cost_date=date(2026, 1, 5),
            category=CostRecord.Category.FEED,
            amount=Decimal("100.00"),
        )
        CostRecord.objects.create(
            herd=self.herd,
            cost_date=date(2026, 1, 6),
            category=CostRecord.Category.FEED,
            amount=Decimal("20.00"),
        )
        CostRecord.objects.create(
            herd=self.herd,
            cost_date=date(2026, 1, 7),
            category=CostRecord.Category.MEDICINE,
            amount=Decimal("50.00"),
        )
        self.assertEqual(
            get_cost_statistics(),
            {"total_cost": "170.00", "by_category": {"feed": "120.00", "medicine": "50.00"}},
        )

    def test_cost_012_date_filtering_and_empty_dataset(self):
        CostRecord.objects.create(
            herd=self.herd,
            cost_date=date(2026, 1, 5),
            category=CostRecord.Category.FEED,
            amount=Decimal("100.00"),
        )
        CostRecord.objects.create(
            herd=self.herd,
            cost_date=date(2026, 2, 5),
            category=CostRecord.Category.CARE,
            amount=Decimal("25.00"),
        )
        self.assertEqual(
            get_cost_statistics(date(2026, 2, 1), date(2026, 2, 28)),
            {"total_cost": "25.00", "by_category": {"care": "25.00"}},
        )
        self.assertEqual(
            get_cost_statistics(date(2026, 3, 1), date(2026, 3, 31)),
            {"total_cost": "0.00", "by_category": {}},
        )

    def test_loss_013_formula_and_multiple_records(self):
        HerdLossRecord.objects.create(
            herd=self.herd,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31),
            opening_quantity=20,
            lost_quantity=2,
        )
        HerdLossRecord.objects.create(
            herd=self.herd,
            period_start=date(2026, 2, 1),
            period_end=date(2026, 2, 28),
            opening_quantity=30,
            lost_quantity=3,
        )
        self.assertEqual(
            get_loss_statistics(),
            {
                "record_count": 2,
                "opening_quantity": 50,
                "lost_quantity": 5,
                "loss_rate_percent": "10.00",
            },
        )

    def test_loss_014_date_containment_and_empty_dataset(self):
        HerdLossRecord.objects.create(
            herd=self.herd,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31),
            opening_quantity=20,
            lost_quantity=2,
        )
        HerdLossRecord.objects.create(
            herd=self.herd,
            period_start=date(2026, 1, 20),
            period_end=date(2026, 2, 5),
            opening_quantity=10,
            lost_quantity=1,
        )
        self.assertEqual(
            get_loss_statistics(date(2026, 1, 1), date(2026, 1, 31)),
            {
                "record_count": 1,
                "opening_quantity": 20,
                "lost_quantity": 2,
                "loss_rate_percent": "10.00",
            },
        )
        self.assertEqual(
            get_loss_statistics(date(2026, 3, 1), date(2026, 3, 31)),
            {
                "record_count": 0,
                "opening_quantity": 0,
                "lost_quantity": 0,
                "loss_rate_percent": None,
            },
        )
