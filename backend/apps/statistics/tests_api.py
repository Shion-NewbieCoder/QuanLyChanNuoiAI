from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from apps.growth.models import GrowthRecord
from apps.herds.models import Herd

from .models import CostRecord, HerdLossRecord


class StatisticsApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="statistics-user",
            password="secretpass123",
        )
        cls.user.groups.add(Group.objects.get(name="quản lý"))
        cls.herd = Herd.objects.create(
            code="HERD-STAT-API",
            name="Statistics API herd",
            animal_type="cattle",
            management_mode="group",
            quantity=20,
            status="active",
        )
        GrowthRecord.objects.create(
            target=cls.herd,
            measurement_date=date(2026, 1, 1),
            weight=Decimal("100.00"),
        )
        CostRecord.objects.create(
            herd=cls.herd,
            cost_date=date(2026, 1, 5),
            category=CostRecord.Category.FEED,
            amount=Decimal("100.00"),
        )
        HerdLossRecord.objects.create(
            herd=cls.herd,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31),
            opening_quantity=20,
            lost_quantity=2,
        )

    def test_api_001_unauthenticated_statistics_are_denied(self):
        for name in ("statistics-growth", "statistics-costs", "statistics-mortality"):
            self.assertIn(self.client.get(reverse(name)).status_code, (401, 403))

    def test_api_002_authenticated_statistics_access_works(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("statistics-growth")).status_code, 200)
        self.assertEqual(self.client.get(reverse("statistics-costs")).status_code, 200)
        self.assertEqual(self.client.get(reverse("statistics-mortality")).status_code, 200)

    def test_api_003_statistics_responses_are_derived_from_sources(self):
        self.client.force_login(self.user)
        self.assertEqual(
            self.client.get(reverse("statistics-growth")).json()["total_weight"],
            "100.00",
        )
        self.assertEqual(
            self.client.get(reverse("statistics-costs")).json()["total_cost"],
            "100.00",
        )
        self.assertEqual(
            self.client.get(reverse("statistics-mortality")).json()["loss_rate_percent"],
            "10.00",
        )

    def test_api_004_invalid_query_parameters_are_rejected(self):
        self.client.force_login(self.user)
        self.assertEqual(
            self.client.get(reverse("statistics-costs"), {"start_date": "not-a-date"}).status_code,
            400,
        )
        self.assertEqual(
            self.client.get(
                reverse("statistics-mortality"),
                {"start_date": "2026-02-01", "end_date": "2026-01-01"},
            ).status_code,
            400,
        )
