from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.domain_validation import DomainValidationService
from apps.herds.models import Animal, AnimalGroup, Herd
from apps.care.models import CareLog
from apps.growth.models import GrowthRecord
from apps.pens.models import Pen
from apps.reproduction.models import ReproductionRecord
from apps.sales.models import SaleRecord
from apps.vaccinations.models import VaccineSchedule


class DomainValidationServiceTests(TestCase):
    def setUp(self):
        self.herd = Herd.objects.create(
            code="HERD-VAL",
            name="Đàn kiểm thử",
            animal_type="bò",
            management_mode="group",
            quantity=12,
            status="active",
        )
        self.animal_group = AnimalGroup.objects.create(
            code="GROUP-VAL",
            name="Nhóm kiểm thử",
            herd=self.herd,
            quantity=4,
            status="active",
        )
        self.animal = Animal.objects.create(
            code="ANIMAL-VAL",
            herd=self.herd,
            status="active",
        )

    def test_pen_valid_herd_target(self):
        pen = Pen(code="PEN-01", name="Chuồng A", status="active", herd=self.herd)
        self.assertTrue(DomainValidationService.validate_pen_target(pen))

    def test_pen_valid_animal_group_target(self):
        pen = Pen(
            code="PEN-02",
            name="Chuồng B",
            status="active",
            animal_group=self.animal_group,
        )
        self.assertTrue(DomainValidationService.validate_pen_target(pen))

    def test_pen_valid_animal_target(self):
        pen = Pen(code="PEN-03", name="Chuồng C", status="active", animal=self.animal)
        self.assertTrue(DomainValidationService.validate_pen_target(pen))

    def test_pen_no_target_invalid(self):
        pen = Pen(code="PEN-04", name="Chuồng D", status="active")
        with self.assertRaises(ValidationError):
            DomainValidationService.validate_pen_target(pen)

    def test_pen_two_targets_invalid(self):
        pen = Pen(
            code="PEN-05",
            name="Chuồng E",
            status="active",
            herd=self.herd,
            animal_group=self.animal_group,
        )
        with self.assertRaises(ValidationError):
            DomainValidationService.validate_pen_target(pen)

    def test_pen_three_targets_invalid(self):
        pen = Pen(
            code="PEN-06",
            name="Chuồng F",
            status="active",
            herd=self.herd,
            animal_group=self.animal_group,
            animal=self.animal,
        )
        with self.assertRaises(ValidationError):
            DomainValidationService.validate_pen_target(pen)

    def test_care_log_herd_target_valid(self):
        care_log = CareLog(herd=self.herd, recorded_at=date(2026, 9, 10), activity="Cho ăn", notes="ok")
        self.assertTrue(DomainValidationService.validate_care_log(care_log))

    def test_growth_record_valid_and_invalid(self):
        valid_record = GrowthRecord(
            target=self.herd,
            measurement_date=date(2026, 9, 8),
            weight=Decimal("120.50"),
        )
        self.assertTrue(DomainValidationService.validate_growth_record(valid_record))

        invalid_record = GrowthRecord(
            target=self.herd,
            measurement_date=date(2026, 9, 8),
            weight=Decimal("-1.00"),
        )
        with self.assertRaises(ValidationError):
            DomainValidationService.validate_growth_record(invalid_record)

    def test_reproduction_record_required_fields(self):
        valid_record = ReproductionRecord(
            target=self.herd,
            event_date=date(2026, 9, 12),
            event_type="đẻ",
        )
        self.assertTrue(DomainValidationService.validate_reproduction_record(valid_record))

        missing_event_type = ReproductionRecord(
            target=self.herd,
            event_date=date(2026, 9, 12),
            event_type="",
        )
        with self.assertRaises(ValidationError):
            DomainValidationService.validate_reproduction_record(missing_event_type)

    def test_sale_record_amount_and_negative_values(self):
        valid_record = SaleRecord(
            target=self.herd,
            sale_date=date(2026, 9, 15),
            quantity=Decimal("12.00"),
            weight=Decimal("540.50"),
            amount=Decimal("2400.00"),
        )
        self.assertTrue(DomainValidationService.validate_sale_record(valid_record))

        negative_amount = SaleRecord(
            target=self.herd,
            sale_date=date(2026, 9, 15),
            quantity=Decimal("12.00"),
            weight=Decimal("540.50"),
            amount=Decimal("-1.00"),
        )
        with self.assertRaises(ValidationError):
            DomainValidationService.validate_sale_record(negative_amount)

    def test_revenue_is_derived_from_sale_amount(self):
        sale = SaleRecord(
            target=self.herd,
            sale_date=date(2026, 9, 15),
            quantity=Decimal("12.00"),
            amount=Decimal("2400.00"),
        )
        self.assertEqual(DomainValidationService.derive_sale_revenue(sale), Decimal("2400.00"))

    def test_vaccine_schedule_valid_status_target_and_date(self):
        valid_schedule = VaccineSchedule(
            target=self.herd,
            vaccine="Vắc xin viêm da",
            scheduled_date=date(2026, 9, 20),
            status=VaccineSchedule.Status.DUE,
        )
        self.assertTrue(DomainValidationService.validate_vaccine_schedule(valid_schedule))

        invalid_status = VaccineSchedule(
            target=self.herd,
            vaccine="Vắc xin viêm da",
            scheduled_date=date(2026, 9, 20),
            status="not-real",
        )
        with self.assertRaises(ValidationError):
            DomainValidationService.validate_vaccine_schedule(invalid_status)
