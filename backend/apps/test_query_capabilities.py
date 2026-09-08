from datetime import date, datetime, timezone
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from rest_framework import filters

from apps.care.models import CareLog, FeedRecord, MedicineRecord
from apps.care.views import CareLogViewSet, FeedRecordViewSet, MedicineRecordViewSet
from apps.growth.models import GrowthRecord
from apps.growth.views import GrowthRecordViewSet
from apps.herds.models import Animal, AnimalGroup, Herd
from apps.herds.views import AnimalGroupViewSet, AnimalViewSet, HerdViewSet
from apps.pens.models import Pen
from apps.pens.views import PenViewSet
from apps.reproduction.models import ReproductionRecord
from apps.reproduction.views import ReproductionRecordViewSet
from apps.sales.models import SaleRecord
from apps.sales.views import SaleRecordViewSet
from apps.users.roles import ROLE_MANAGEMENT
from apps.vaccinations.models import VaccinationRecord, VaccineSchedule
from apps.vaccinations.views import VaccinationRecordViewSet, VaccineScheduleViewSet
from config.filters import ExactFieldFilterBackend


class BusinessApiQueryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        manager_group = Group.objects.get(name=ROLE_MANAGEMENT)
        cls.manager = get_user_model().objects.create_user(username="query-manager")
        cls.manager.groups.add(manager_group)
        cls.no_role_user = get_user_model().objects.create_user(username="query-no-role")

        cls.alpha = Herd.objects.create(
            code="HERD-ALPHA",
            name="Alpha Dairy Herd",
            animal_type="cattle",
            management_mode="group",
            quantity=20,
            status="active",
        )
        cls.beta = Herd.objects.create(
            code="HERD-BETA",
            name="Beta Goat Herd",
            animal_type="goat",
            management_mode="individual",
            quantity=5,
            status="inactive",
        )
        cls.animal = Animal.objects.create(code="ANIMAL-ALPHA", herd=cls.alpha, status="active")
        cls.animal_group = AnimalGroup.objects.create(
            code="GROUP-ALPHA",
            name="Alpha Group",
            herd=cls.alpha,
            quantity=4,
            status="active",
        )
        cls.pen = Pen.objects.create(
            code="PEN-ALPHA",
            name="Alpha Pen",
            status="active",
            herd=cls.alpha,
        )

        cls.care_early = CareLog.objects.create(
            herd=cls.alpha,
            recorded_at=datetime(2026, 1, 1, 8, tzinfo=timezone.utc),
            activity="Clean alpha shelter",
            notes="Morning care",
        )
        cls.care_late = CareLog.objects.create(
            herd=cls.alpha,
            recorded_at=datetime(2026, 1, 3, 8, tzinfo=timezone.utc),
            activity="Inspect alpha shelter",
            notes="Afternoon care",
        )
        cls.other_care = CareLog.objects.create(
            herd=cls.beta,
            recorded_at=datetime(2026, 1, 2, 8, tzinfo=timezone.utc),
            activity="Clean beta shelter",
        )
        cls.feed = FeedRecord.objects.create(
            herd=cls.alpha,
            recorded_at=datetime(2026, 1, 1, 9, tzinfo=timezone.utc),
            feed_type="Fresh grass",
            quantity=Decimal("12.00"),
            notes="Alpha ration",
        )
        cls.medicine = MedicineRecord.objects.create(
            herd=cls.alpha,
            recorded_at=datetime(2026, 1, 1, 10, tzinfo=timezone.utc),
            medicine="Vitamin Alpha",
            dose=Decimal("2.00"),
            notes="Observe herd",
        )

        cls.schedule = VaccineSchedule.objects.create(
            target=cls.alpha,
            vaccine="Alpha vaccine",
            scheduled_date=date(2026, 2, 1),
            status=VaccineSchedule.Status.SCHEDULED,
        )
        cls.due_schedule = VaccineSchedule.objects.create(
            target=cls.beta,
            vaccine="Beta vaccine",
            scheduled_date=date(2026, 2, 2),
            status=VaccineSchedule.Status.DUE,
        )
        cls.vaccination = VaccinationRecord.objects.create(
            schedule=cls.schedule,
            actual_date=date(2026, 2, 1),
            notes="Alpha vaccination completed",
        )

        cls.growth_late = GrowthRecord.objects.create(
            target=cls.alpha,
            measurement_date=date(2026, 3, 3),
            weight=Decimal("120.00"),
            notes="Late measurement",
        )
        cls.growth_early = GrowthRecord.objects.create(
            target=cls.alpha,
            measurement_date=date(2026, 3, 1),
            weight=Decimal("100.00"),
            notes="Early measurement",
        )
        cls.reproduction = ReproductionRecord.objects.create(
            target=cls.alpha,
            event_date=date(2026, 4, 1),
            event_type="Birth",
            result="Successful",
            notes="Healthy offspring",
        )
        cls.sale_late = SaleRecord.objects.create(
            target=cls.alpha,
            sale_date=date(2026, 5, 3),
            amount=Decimal("300.00"),
            notes="Alpha sale late",
        )
        cls.sale_early = SaleRecord.objects.create(
            target=cls.alpha,
            sale_date=date(2026, 5, 1),
            amount=Decimal("100.00"),
            notes="Alpha sale early",
        )

    def setUp(self):
        self.client.force_login(self.manager)

    def assert_ids(self, response, expected):
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.json()], expected)

    def test_query_001_all_target_resources_declare_restricted_query_fields(self):
        expected = {
            HerdViewSet: (
                {"code", "name", "animal_type", "status"},
                {"status", "animal_type", "management_mode"},
                {"code", "name", "quantity"},
            ),
            AnimalViewSet: ({"code", "status"}, {"herd", "status"}, {"code"}),
            AnimalGroupViewSet: (
                {"code", "name", "status"},
                {"herd", "status"},
                {"code", "name", "quantity"},
            ),
            PenViewSet: (
                {"code", "name", "location", "description", "status"},
                {"herd", "animal_group", "animal", "status"},
                {"code", "name"},
            ),
            CareLogViewSet: ({"activity", "notes"}, {"herd"}, {"recorded_at"}),
            FeedRecordViewSet: (
                {"feed_type", "notes"},
                {"herd"},
                {"recorded_at", "quantity"},
            ),
            MedicineRecordViewSet: (
                {"medicine", "notes"},
                {"herd"},
                {"recorded_at", "dose"},
            ),
            VaccineScheduleViewSet: (
                {"vaccine"},
                {"target", "status"},
                {"scheduled_date", "vaccine"},
            ),
            VaccinationRecordViewSet: ({"notes"}, {"schedule"}, {"actual_date"}),
            GrowthRecordViewSet: (
                {"notes"},
                {"target"},
                {"measurement_date", "weight"},
            ),
            ReproductionRecordViewSet: (
                {"event_type", "result", "notes"},
                {"target"},
                {"event_date"},
            ),
            SaleRecordViewSet: ({"notes"}, {"target"}, {"sale_date", "amount"}),
        }

        for viewset, (search_fields, exact_fields, ordering_fields) in expected.items():
            with self.subTest(viewset=viewset.__name__):
                self.assertEqual(
                    viewset.filter_backends,
                    [filters.SearchFilter, ExactFieldFilterBackend, filters.OrderingFilter],
                )
                self.assertEqual(set(viewset.search_fields), search_fields)
                self.assertEqual(set(viewset.exact_filter_fields), exact_fields)
                self.assertEqual(set(viewset.ordering_fields), ordering_fields)

    def test_query_002_herd_text_search_returns_only_match(self):
        response = self.client.get(reverse("herd-list"), {"search": "Alpha Dairy"})
        self.assert_ids(response, [self.alpha.pk])

    def test_query_003_care_and_medicine_text_search_work(self):
        cases = (
            ("carelog-list", "Inspect alpha", self.care_late.pk),
            ("medicinerecord-list", "Vitamin Alpha", self.medicine.pk),
        )
        for route, term, expected_id in cases:
            with self.subTest(route=route):
                response = self.client.get(reverse(route), {"search": term})
                self.assert_ids(response, [expected_id])

    def test_query_004_nonmatching_search_returns_empty_list(self):
        response = self.client.get(reverse("herd-list"), {"search": "not-present"})
        self.assert_ids(response, [])

    def test_query_005_search_does_not_bypass_rbac(self):
        self.client.force_login(self.no_role_user)
        response = self.client.get(reverse("herd-list"), {"search": "Alpha"})
        self.assertEqual(response.status_code, 403)

    def test_query_006_herd_status_and_type_exact_filters_work(self):
        response = self.client.get(
            reverse("herd-list"),
            {"status": "active", "animal_type": "cattle"},
        )
        self.assert_ids(response, [self.alpha.pk])

    def test_query_007_dependent_relation_filter_isolates_herd(self):
        response = self.client.get(reverse("carelog-list"), {"herd": self.alpha.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {item["id"] for item in response.json()},
            {self.care_early.pk, self.care_late.pk},
        )

    def test_query_008_vaccine_schedule_status_filter_works(self):
        response = self.client.get(
            reverse("vaccineschedule-list"),
            {"status": VaccineSchedule.Status.DUE},
        )
        self.assert_ids(response, [self.due_schedule.pk])

    def test_query_009_invalid_relation_is_safe_and_missing_relation_is_empty(self):
        invalid = self.client.get(reverse("carelog-list"), {"herd": "not-an-integer"})
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(invalid.json()["error_code"], "validation_error")
        self.assertIn("herd", invalid.json()["field_errors"])

        missing = self.client.get(reverse("carelog-list"), {"herd": 999999})
        self.assert_ids(missing, [])

    def test_query_010_empty_search_filter_and_unknown_ordering_are_safe(self):
        response = self.client.get(
            reverse("herd-list"),
            {"search": "", "status": "", "ordering": "unknown"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual({item["id"] for item in response.json()}, {self.alpha.pk, self.beta.pk})

    def test_query_011_ascending_and_descending_ordering_work(self):
        ascending = self.client.get(reverse("herd-list"), {"ordering": "quantity"})
        self.assert_ids(ascending, [self.beta.pk, self.alpha.pk])

        descending = self.client.get(reverse("herd-list"), {"ordering": "-quantity"})
        self.assert_ids(descending, [self.alpha.pk, self.beta.pk])

    def test_query_012_growth_measurement_date_ordering_works(self):
        response = self.client.get(
            reverse("growthrecord-list"),
            {"target": self.alpha.pk, "ordering": "measurement_date"},
        )
        self.assert_ids(response, [self.growth_early.pk, self.growth_late.pk])

    def test_query_013_sale_amount_and_date_ordering_work(self):
        by_amount = self.client.get(
            reverse("salerecord-list"),
            {"target": self.alpha.pk, "ordering": "amount"},
        )
        self.assert_ids(by_amount, [self.sale_early.pk, self.sale_late.pk])

        by_date_descending = self.client.get(
            reverse("salerecord-list"),
            {"target": self.alpha.pk, "ordering": "-sale_date"},
        )
        self.assert_ids(by_date_descending, [self.sale_late.pk, self.sale_early.pk])

    def test_query_014_ordering_does_not_bypass_rbac(self):
        self.client.force_login(self.no_role_user)
        response = self.client.get(reverse("salerecord-list"), {"ordering": "amount"})
        self.assertEqual(response.status_code, 403)

    def test_query_015_search_and_filter_can_be_combined(self):
        response = self.client.get(
            reverse("herd-list"),
            {"search": "Alpha", "status": "active", "management_mode": "group"},
        )
        self.assert_ids(response, [self.alpha.pk])

        excluded = self.client.get(
            reverse("herd-list"),
            {"search": "Alpha", "status": "inactive"},
        )
        self.assert_ids(excluded, [])

    def test_query_016_filter_and_ordering_can_be_combined(self):
        response = self.client.get(
            reverse("carelog-list"),
            {"herd": self.alpha.pk, "ordering": "recorded_at"},
        )
        self.assert_ids(response, [self.care_early.pk, self.care_late.pk])

    def test_query_017_existing_crud_behavior_remains_available(self):
        detail = self.client.get(reverse("herd-detail", args=[self.alpha.pk]))
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["code"], "HERD-ALPHA")

        created = self.client.post(
            reverse("herd-list"),
            {
                "code": "HERD-GAMMA",
                "name": "Gamma Herd",
                "animal_type": "cattle",
                "management_mode": "group",
                "quantity": 3,
                "status": "active",
            },
            content_type="application/json",
        )
        self.assertEqual(created.status_code, 201)
