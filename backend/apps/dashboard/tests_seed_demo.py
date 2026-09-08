from datetime import date, timedelta
from decimal import Decimal
from io import StringIO
from unittest.mock import patch

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from apps.ai.growth_report import select_growth_facts
from apps.ai.herd_summary import build_herd_summary_facts
from apps.ai.reminders import select_reminder_sources
from apps.care.models import CareLog, FeedRecord, MedicineRecord
from apps.domain_validation import derive_sales_revenue
from apps.growth.models import GrowthRecord
from apps.herds.models import Animal, AnimalGroup, Herd
from apps.pens.models import Pen
from apps.reproduction.models import ReproductionRecord
from apps.sales.models import SaleRecord
from apps.statistics.models import CostRecord, HerdLossRecord
from apps.statistics.services import (
    get_cost_statistics,
    get_growth_statistics,
    get_loss_statistics,
)
from apps.users.roles import ROLE_EMPLOYEE, ROLE_MANAGEMENT, ROLE_TECHNICIAN
from apps.vaccinations.models import VaccinationRecord, VaccineSchedule
from apps.vaccinations.serializers import get_alert_classification

from .management.commands.seed_demo import DEMO_PASSWORD, DEMO_USERS


EXPECTED_COUNTS = {
    "herds": 2,
    "animal_groups": 2,
    "animals": 2,
    "pens": 3,
    "care_logs": 2,
    "feed_records": 2,
    "medicine_records": 2,
    "vaccine_schedules": 4,
    "vaccination_records": 1,
    "growth_records": 3,
    "reproduction_records": 1,
    "sale_records": 2,
    "loss_records": 2,
    "cost_records": 5,
    "demo_users": 3,
}


def reserved_counts():
    schedules = VaccineSchedule.objects.filter(vaccine__startswith="DEMO-VACCINE-")
    return {
        "herds": Herd.objects.filter(code__in=("DEMO-HERD-001", "DEMO-HERD-002")).count(),
        "animal_groups": AnimalGroup.objects.filter(code__startswith="DEMO-GROUP-").count(),
        "animals": Animal.objects.filter(code__startswith="DEMO-ANIMAL-").count(),
        "pens": Pen.objects.filter(code__startswith="DEMO-PEN-").count(),
        "care_logs": CareLog.objects.filter(activity__startswith="DEMO-CARE-").count(),
        "feed_records": FeedRecord.objects.filter(feed_type__startswith="DEMO-FEED-").count(),
        "medicine_records": MedicineRecord.objects.filter(
            medicine__startswith="DEMO-MEDICINE-"
        ).count(),
        "vaccine_schedules": schedules.count(),
        "vaccination_records": VaccinationRecord.objects.filter(schedule__in=schedules).count(),
        "growth_records": GrowthRecord.objects.filter(notes__startswith="DEMO-GROWTH-").count(),
        "reproduction_records": ReproductionRecord.objects.filter(
            notes__startswith="DEMO-REPRODUCTION-"
        ).count(),
        "sale_records": SaleRecord.objects.filter(notes__startswith="DEMO-SALE-").count(),
        "loss_records": HerdLossRecord.objects.filter(notes__startswith="DEMO-LOSS-").count(),
        "cost_records": CostRecord.objects.filter(notes__startswith="DEMO-COST-").count(),
        "demo_users": get_user_model().objects.filter(username__in=DEMO_USERS).count(),
    }


@override_settings(DEBUG=True)
class SeedDemoCommandTests(TestCase):
    anchor = date(2026, 9, 8)

    def run_seed(self, anchor=None):
        output = StringIO()
        with patch(
            "apps.dashboard.management.commands.seed_demo.timezone.localdate",
            return_value=anchor or self.anchor,
        ):
            call_command("seed_demo", stdout=output)
        return output.getvalue()

    @patch("apps.ai.reminders.get_configured_provider")
    @patch("apps.ai.herd_summary.get_configured_provider")
    @patch("apps.ai.growth_report.get_configured_provider")
    def test_seed_creates_exact_valid_reserved_dataset_without_calling_ai(
        self, growth_provider, summary_provider, reminder_provider
    ):
        output = self.run_seed()
        self.assertIn("local DEBUG use only", output)
        self.assertEqual(reserved_counts(), EXPECTED_COUNTS)
        reminder_provider.assert_not_called()
        summary_provider.assert_not_called()
        growth_provider.assert_not_called()

        for model, lookup in (
            (Herd, {"code__startswith": "DEMO-HERD-"}),
            (AnimalGroup, {"code__startswith": "DEMO-GROUP-"}),
            (Animal, {"code__startswith": "DEMO-ANIMAL-"}),
            (Pen, {"code__startswith": "DEMO-PEN-"}),
            (CareLog, {"activity__startswith": "DEMO-CARE-"}),
            (FeedRecord, {"feed_type__startswith": "DEMO-FEED-"}),
            (MedicineRecord, {"medicine__startswith": "DEMO-MEDICINE-"}),
            (VaccineSchedule, {"vaccine__startswith": "DEMO-VACCINE-"}),
            (GrowthRecord, {"notes__startswith": "DEMO-GROWTH-"}),
            (ReproductionRecord, {"notes__startswith": "DEMO-REPRODUCTION-"}),
            (SaleRecord, {"notes__startswith": "DEMO-SALE-"}),
            (HerdLossRecord, {"notes__startswith": "DEMO-LOSS-"}),
            (CostRecord, {"notes__startswith": "DEMO-COST-"}),
        ):
            for instance in model.objects.filter(**lookup):
                with self.subTest(model=model.__name__, pk=instance.pk):
                    instance.full_clean()

        target_counts = sorted(
            sum(target is not None for target in (pen.herd_id, pen.animal_group_id, pen.animal_id))
            for pen in Pen.objects.filter(code__startswith="DEMO-PEN-")
        )
        self.assertEqual(target_counts, [1, 1, 1])
        self.assertEqual(
            {
                "herd": Pen.objects.filter(code="DEMO-PEN-HERD").get().herd_id is not None,
                "group": Pen.objects.filter(code="DEMO-PEN-GROUP").get().animal_group_id
                is not None,
                "animal": Pen.objects.filter(code="DEMO-PEN-ANIMAL").get().animal_id
                is not None,
            },
            {"herd": True, "group": True, "animal": True},
        )

    def test_demo_users_roles_password_and_safety_state_are_exact(self):
        self.run_seed()
        for username, role in DEMO_USERS.items():
            user = get_user_model().objects.get(username=username)
            with self.subTest(username=username):
                self.assertTrue(user.is_active)
                self.assertFalse(user.is_staff)
                self.assertFalse(user.is_superuser)
                self.assertTrue(user.check_password(DEMO_PASSWORD))
                self.assertEqual(list(user.groups.values_list("name", flat=True)), [role])
        self.assertEqual(
            set(Group.objects.filter(name__in=DEMO_USERS.values()).values_list("name", flat=True)),
            {ROLE_MANAGEMENT, ROLE_TECHNICIAN, ROLE_EMPLOYEE},
        )

    def test_relative_dates_vaccine_statuses_and_approved_growth_values(self):
        self.run_seed()
        schedules = {
            schedule.vaccine: schedule
            for schedule in VaccineSchedule.objects.filter(vaccine__startswith="DEMO-VACCINE-")
        }
        self.assertEqual(schedules["DEMO-VACCINE-OVERDUE"].scheduled_date, self.anchor - timedelta(days=7))
        self.assertEqual(schedules["DEMO-VACCINE-OVERDUE"].status, VaccineSchedule.Status.DUE)
        self.assertEqual(get_alert_classification(schedules["DEMO-VACCINE-OVERDUE"], self.anchor), "overdue")
        self.assertEqual(schedules["DEMO-VACCINE-TODAY"].scheduled_date, self.anchor)
        self.assertEqual(get_alert_classification(schedules["DEMO-VACCINE-TODAY"], self.anchor), "due today")
        self.assertEqual(schedules["DEMO-VACCINE-FUTURE"].scheduled_date, self.anchor + timedelta(days=30))
        self.assertEqual(schedules["DEMO-VACCINE-FUTURE"].status, VaccineSchedule.Status.SCHEDULED)
        completed = schedules["DEMO-VACCINE-COMPLETED"]
        self.assertEqual(completed.scheduled_date, self.anchor - timedelta(days=30))
        self.assertEqual(completed.status, VaccineSchedule.Status.COMPLETED)
        self.assertEqual(completed.records.get().actual_date, self.anchor - timedelta(days=30))

        growth = list(
            GrowthRecord.objects.filter(notes__startswith="DEMO-GROWTH-").order_by(
                "measurement_date"
            )
        )
        self.assertEqual(
            [(row.measurement_date, row.weight) for row in growth],
            [
                (self.anchor - timedelta(days=60), Decimal("100.00")),
                (self.anchor - timedelta(days=30), Decimal("112.00")),
                (self.anchor, Decimal("125.00")),
            ],
        )

    def test_statistics_revenue_and_ai_factual_sources_are_non_empty(self):
        self.run_seed()
        primary = Herd.objects.get(code="DEMO-HERD-001")
        self.assertEqual(get_growth_statistics()["record_count"], 3)
        self.assertEqual(get_cost_statistics()["total_cost"], "6500000.00")
        self.assertIsNotNone(get_loss_statistics()["loss_rate_percent"])
        self.assertEqual(
            derive_sales_revenue(SaleRecord.objects.filter(target=primary)),
            Decimal("12500000.00"),
        )
        self.assertEqual(len(select_reminder_sources("herd", primary.pk)), 3)
        summary_facts, source_count = build_herd_summary_facts(primary)
        self.assertEqual(
            {key: len(value) for key, value in summary_facts.items() if key != "herd"},
            {
                "care_logs": 2,
                "feed_records": 2,
                "medicine_records": 2,
                "vaccine_schedules": 4,
                "vaccination_records": 1,
            },
        )
        self.assertEqual(source_count, 11)
        self.assertEqual(len(select_growth_facts(primary)), 3)
        self.assertFalse(
            any(model.__name__ in {"AIRequest", "AIResponse"} for model in apps.get_models())
        )

    def test_second_run_restores_demo_data_refreshes_dates_and_preserves_non_demo_rows(self):
        normal_herd = Herd.objects.create(
            code="NORMAL-HERD-001",
            name="Non-demo herd",
            animal_type="goat",
            management_mode="group",
            quantity=7,
            status="active",
        )
        normal_user = get_user_model().objects.create_user(
            username="normal-user",
            password="normal-password",
        )
        self.run_seed(self.anchor)
        primary = Herd.objects.get(code="DEMO-HERD-001")
        primary.name = "Changed demo value"
        primary.quantity = 1
        primary.save()
        growth = GrowthRecord.objects.get(notes="DEMO-GROWTH-001")
        growth.weight = Decimal("999.00")
        growth.save()
        manager = get_user_model().objects.get(username="demo_manager")
        manager.groups.add(Group.objects.get(name=ROLE_EMPLOYEE))
        manager.set_password("changed-password")
        manager.save()

        next_anchor = self.anchor + timedelta(days=1)
        self.run_seed(next_anchor)
        self.assertEqual(reserved_counts(), EXPECTED_COUNTS)
        primary.refresh_from_db()
        self.assertEqual((primary.name, primary.quantity), ("Đàn bò demo chính", 100))
        growth.refresh_from_db()
        self.assertEqual(growth.weight, Decimal("100.00"))
        self.assertEqual(growth.measurement_date, next_anchor - timedelta(days=60))
        manager.refresh_from_db()
        self.assertTrue(manager.check_password(DEMO_PASSWORD))
        self.assertEqual(
            set(manager.groups.values_list("name", flat=True)),
            {ROLE_MANAGEMENT},
        )
        normal_herd.refresh_from_db()
        normal_user.refresh_from_db()
        self.assertEqual((normal_herd.name, normal_herd.quantity), ("Non-demo herd", 7))
        self.assertTrue(normal_user.check_password("normal-password"))


class SeedDemoProductionGuardTests(TestCase):
    @override_settings(DEBUG=False)
    def test_debug_false_refuses_before_any_demo_write(self):
        with self.assertRaisesRegex(CommandError, "DEBUG=True"):
            call_command("seed_demo", stdout=StringIO())
        self.assertEqual(reserved_counts(), {key: 0 for key in EXPECTED_COUNTS})
