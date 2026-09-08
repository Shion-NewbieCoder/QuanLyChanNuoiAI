from datetime import datetime, time, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.care.models import CareLog, FeedRecord, MedicineRecord
from apps.growth.models import GrowthRecord
from apps.herds.models import Animal, AnimalGroup, Herd
from apps.pens.models import Pen
from apps.reproduction.models import ReproductionRecord
from apps.sales.models import SaleRecord
from apps.statistics.models import CostRecord, HerdLossRecord
from apps.users.roles import ROLE_EMPLOYEE, ROLE_MANAGEMENT, ROLE_NAMES, ROLE_TECHNICIAN
from apps.vaccinations.models import VaccinationRecord, VaccineSchedule


DEMO_PASSWORD = "DemoOnly-2026!"
DEMO_USERS = {
    "demo_manager": ROLE_MANAGEMENT,
    "demo_technician": ROLE_TECHNICIAN,
    "demo_employee": ROLE_EMPLOYEE,
}


def _validated_upsert(model, lookup, defaults):
    matches = model.objects.filter(**lookup).order_by("pk")
    instance = matches.first()
    if instance is None:
        instance = model(**lookup)
    for field_name, value in defaults.items():
        setattr(instance, field_name, value)
    instance.full_clean()
    instance.save()
    matches.exclude(pk=instance.pk).delete()
    return instance


def _local_datetime(day, hour):
    return timezone.make_aware(datetime.combine(day, time(hour=hour)))


class Command(BaseCommand):
    help = "Create or restore the local-only deterministic academic demo dataset."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_demo is restricted to local demo use with DEBUG=True.")

        anchor_date = timezone.localdate()
        with transaction.atomic():
            groups = {role: Group.objects.get_or_create(name=role)[0] for role in ROLE_NAMES}
            self._seed_users(groups)
            primary_herd, secondary_herd = self._seed_herds()
            groups_by_code, animals_by_code = self._seed_animals(
                primary_herd, secondary_herd
            )
            self._seed_pens(primary_herd, groups_by_code, animals_by_code)
            self._seed_care(primary_herd, anchor_date)
            completed_schedule = self._seed_vaccines(primary_herd, anchor_date)
            self._seed_vaccination_record(completed_schedule, anchor_date)
            self._seed_growth(primary_herd, anchor_date)
            self._seed_reproduction(primary_herd, anchor_date)
            self._seed_sales(primary_herd, anchor_date)
            self._seed_losses(primary_herd, anchor_date)
            self._seed_costs(primary_herd, anchor_date)

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo dataset ready for {anchor_date.isoformat()} (local DEBUG use only)."
            )
        )

    def _seed_users(self, groups):
        user_model = get_user_model()
        recognized_groups = list(Group.objects.filter(name__in=ROLE_NAMES))
        for username, role in DEMO_USERS.items():
            user, _ = user_model.objects.get_or_create(username=username)
            user.is_active = True
            user.is_staff = False
            user.is_superuser = False
            user.set_password(DEMO_PASSWORD)
            user.full_clean()
            user.save()
            user.groups.remove(*recognized_groups)
            user.groups.add(groups[role])

    def _seed_herds(self):
        primary = _validated_upsert(
            Herd,
            {"code": "DEMO-HERD-001"},
            {
                "name": "Đàn bò demo chính",
                "animal_type": "bò",
                "management_mode": "group",
                "quantity": 100,
                "status": "active",
            },
        )
        secondary = _validated_upsert(
            Herd,
            {"code": "DEMO-HERD-002"},
            {
                "name": "Đàn bò demo đối chiếu",
                "animal_type": "bò",
                "management_mode": "individual",
                "quantity": 20,
                "status": "active",
            },
        )
        return primary, secondary

    def _seed_animals(self, primary, secondary):
        group_specs = (
            ("DEMO-GROUP-001", "Nhóm demo chính", primary, 50),
            ("DEMO-GROUP-002", "Nhóm demo đối chiếu", secondary, 10),
        )
        groups = {
            code: _validated_upsert(
                AnimalGroup,
                {"code": code},
                {"name": name, "herd": herd, "quantity": quantity, "status": "active"},
            )
            for code, name, herd, quantity in group_specs
        }
        animal_specs = (
            ("DEMO-ANIMAL-001", primary),
            ("DEMO-ANIMAL-002", secondary),
        )
        animals = {
            code: _validated_upsert(
                Animal,
                {"code": code},
                {"herd": herd, "status": "active"},
            )
            for code, herd in animal_specs
        }
        return groups, animals

    def _seed_pens(self, primary, groups, animals):
        specs = (
            (
                "DEMO-PEN-HERD",
                "Chuồng demo theo đàn",
                {"herd": primary, "animal_group": None, "animal": None},
            ),
            (
                "DEMO-PEN-GROUP",
                "Chuồng demo theo nhóm",
                {
                    "herd": None,
                    "animal_group": groups["DEMO-GROUP-001"],
                    "animal": None,
                },
            ),
            (
                "DEMO-PEN-ANIMAL",
                "Chuồng demo theo cá thể",
                {
                    "herd": None,
                    "animal_group": None,
                    "animal": animals["DEMO-ANIMAL-001"],
                },
            ),
        )
        for code, name, targets in specs:
            _validated_upsert(
                Pen,
                {"code": code},
                {
                    "name": name,
                    "location": "Khu demo",
                    "description": "Dữ liệu minh họa TSK-027",
                    "status": "active",
                    **targets,
                },
            )

    def _seed_care(self, herd, anchor):
        for marker, days, activity in (
            ("DEMO-CARE-001", 12, "Kiểm tra tổng quát"),
            ("DEMO-CARE-002", 5, "Vệ sinh khu chăn nuôi"),
        ):
            _validated_upsert(
                CareLog,
                {"herd": herd, "activity": marker},
                {
                    "recorded_at": _local_datetime(anchor - timedelta(days=days), 8),
                    "notes": activity,
                },
            )
        for marker, days, quantity, description in (
            ("DEMO-FEED-001", 10, "250.00", "Khẩu phần cỏ khô"),
            ("DEMO-FEED-002", 3, "180.00", "Khẩu phần thức ăn hỗn hợp"),
        ):
            _validated_upsert(
                FeedRecord,
                {"herd": herd, "feed_type": marker},
                {
                    "recorded_at": _local_datetime(anchor - timedelta(days=days), 9),
                    "quantity": Decimal(quantity),
                    "notes": description,
                },
            )
        for marker, days, dose, description in (
            ("DEMO-MEDICINE-001", 9, "5.00", "Vitamin bổ sung"),
            ("DEMO-MEDICINE-002", 2, "3.00", "Thuốc demo theo dõi"),
        ):
            _validated_upsert(
                MedicineRecord,
                {"herd": herd, "medicine": marker},
                {
                    "recorded_at": _local_datetime(anchor - timedelta(days=days), 10),
                    "dose": Decimal(dose),
                    "notes": description,
                },
            )

    def _seed_vaccines(self, herd, anchor):
        specs = (
            ("DEMO-VACCINE-OVERDUE", -7, VaccineSchedule.Status.DUE),
            ("DEMO-VACCINE-TODAY", 0, VaccineSchedule.Status.DUE),
            ("DEMO-VACCINE-FUTURE", 30, VaccineSchedule.Status.SCHEDULED),
            ("DEMO-VACCINE-COMPLETED", -30, VaccineSchedule.Status.COMPLETED),
        )
        schedules = {}
        for vaccine, offset, status in specs:
            schedules[vaccine] = _validated_upsert(
                VaccineSchedule,
                {"target": herd, "vaccine": vaccine},
                {"scheduled_date": anchor + timedelta(days=offset), "status": status},
            )
        return schedules["DEMO-VACCINE-COMPLETED"]

    def _seed_vaccination_record(self, completed_schedule, anchor):
        records = VaccinationRecord.objects.filter(schedule=completed_schedule).order_by("pk")
        record = records.first() or VaccinationRecord(schedule=completed_schedule)
        record.actual_date = anchor - timedelta(days=30)
        record.notes = "DEMO-VACCINATION-001"
        record.full_clean()
        record.save()
        records.exclude(pk=record.pk).delete()

    def _seed_growth(self, herd, anchor):
        for marker, offset, weight in (
            ("DEMO-GROWTH-001", -60, "100.00"),
            ("DEMO-GROWTH-002", -30, "112.00"),
            ("DEMO-GROWTH-003", 0, "125.00"),
        ):
            _validated_upsert(
                GrowthRecord,
                {"target": herd, "notes": marker},
                {
                    "measurement_date": anchor + timedelta(days=offset),
                    "weight": Decimal(weight),
                },
            )

    def _seed_reproduction(self, herd, anchor):
        _validated_upsert(
            ReproductionRecord,
            {"target": herd, "notes": "DEMO-REPRODUCTION-001"},
            {
                "event_date": anchor - timedelta(days=45),
                "event_type": "breeding",
                "result": "recorded",
            },
        )

    def _seed_sales(self, herd, anchor):
        for marker, offset, amount in (
            ("DEMO-SALE-001", -40, "5000000.00"),
            ("DEMO-SALE-002", -20, "7500000.00"),
        ):
            _validated_upsert(
                SaleRecord,
                {"target": herd, "notes": marker},
                {
                    "sale_date": anchor + timedelta(days=offset),
                    "quantity": None,
                    "weight": None,
                    "amount": Decimal(amount),
                },
            )

    def _seed_losses(self, herd, anchor):
        specs = (
            ("DEMO-LOSS-001", -90, -61, 100, 2),
            ("DEMO-LOSS-002", -60, -31, 98, 1),
        )
        for marker, start_offset, end_offset, opening, lost in specs:
            _validated_upsert(
                HerdLossRecord,
                {"herd": herd, "notes": marker},
                {
                    "period_start": anchor + timedelta(days=start_offset),
                    "period_end": anchor + timedelta(days=end_offset),
                    "opening_quantity": opening,
                    "lost_quantity": lost,
                },
            )

    def _seed_costs(self, herd, anchor):
        specs = (
            (CostRecord.Category.FEED, -25, "3000000.00"),
            (CostRecord.Category.MEDICINE, -20, "1200000.00"),
            (CostRecord.Category.VACCINE, -15, "800000.00"),
            (CostRecord.Category.CARE, -10, "1000000.00"),
            (CostRecord.Category.OTHER, -5, "500000.00"),
        )
        for category, offset, amount in specs:
            _validated_upsert(
                CostRecord,
                {"herd": herd, "notes": f"DEMO-COST-{category.upper()}"},
                {
                    "cost_date": anchor + timedelta(days=offset),
                    "category": category,
                    "amount": Decimal(amount),
                },
            )
