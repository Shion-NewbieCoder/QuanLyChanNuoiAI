from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from apps.herds.models import Herd

from .models import GrowthRecord


class GrowthApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="growth-manager",
            password="secretpass123",
        )
        cls.user.groups.add(Group.objects.get(name="quản lý"))
        cls.herd = Herd.objects.create(
            code="HERD-001",
            name="Đàn bò sữa",
            animal_type="bò",
            management_mode="group",
            quantity=12,
            status="active",
        )
        cls.record = GrowthRecord.objects.create(
            target=cls.herd,
            measurement_date=date(2026, 9, 10),
            weight=Decimal("120.50"),
            notes="Cân nặng đầu tháng",
        )

    def test_api_001_unauthenticated_denied(self):
        response = self.client.get(reverse("growthrecord-list"))
        self.assertIn(response.status_code, (401, 403))

    def test_api_002_authenticated_list_and_retrieve(self):
        self.client.force_login(self.user)
        list_response = self.client.get(reverse("growthrecord-list"))
        self.assertEqual(list_response.status_code, 200)
        self.assertTrue(len(list_response.json()) >= 1)

        detail_response = self.client.get(reverse("growthrecord-detail", args=[self.record.pk]))
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["weight"], "120.50")

    def test_api_003_valid_growth_create(self):
        self.client.force_login(self.user)
        payload = {
            "target": self.herd.pk,
            "measurement_date": "2026-09-11",
            "weight": "130.75",
            "notes": "Cân nặng mới",
        }
        response = self.client.post(reverse("growthrecord-list"), payload, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(GrowthRecord.objects.filter(weight=Decimal("130.75")).exists())

    def test_api_004_invalid_growth_create(self):
        self.client.force_login(self.user)
        payload = {
            "target": 999999,
            "measurement_date": "2026-09-11",
            "weight": "130.75",
            "notes": "Sai target",
        }
        response = self.client.post(reverse("growthrecord-list"), payload, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_api_005_growth_update_and_delete(self):
        self.client.force_login(self.user)
        update_response = self.client.patch(
            reverse("growthrecord-detail", args=[self.record.pk]),
            {"weight": "135.00"},
            content_type="application/json",
        )
        self.assertEqual(update_response.status_code, 200)

        delete_response = self.client.delete(reverse("growthrecord-detail", args=[self.record.pk]))
        self.assertEqual(delete_response.status_code, 204)

    def test_api_006_negative_growth_weight_rejected(self):
        self.client.force_login(self.user)
        payload = {
            "target": self.herd.pk,
            "measurement_date": "2026-09-12",
            "weight": "-1.00",
            "notes": "Sai",
        }
        response = self.client.post(reverse("growthrecord-list"), payload, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_api_007_missing_object_returns_404(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("growthrecord-detail", args=[999999]))
        self.assertEqual(response.status_code, 404)
