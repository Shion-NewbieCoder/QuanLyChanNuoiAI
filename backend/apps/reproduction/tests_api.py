from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from apps.herds.models import Herd

from .models import ReproductionRecord


class ReproductionApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="reproduction-manager",
            password="secretpass123",
        )
        cls.user.groups.add(Group.objects.get(name="quản lý"))
        cls.herd = Herd.objects.create(
            code="HERD-002",
            name="Đàn lợn nái",
            animal_type="lợn",
            management_mode="group",
            quantity=18,
            status="active",
        )
        cls.record = ReproductionRecord.objects.create(
            target=cls.herd,
            event_date=date(2026, 9, 12),
            event_type="đẻ",
            result="thành công",
            notes="Lợn nái khỏe mạnh",
        )

    def test_api_001_unauthenticated_denied(self):
        response = self.client.get(reverse("reproductionrecord-list"))
        self.assertIn(response.status_code, (401, 403))

    def test_api_002_authenticated_list_and_retrieve(self):
        self.client.force_login(self.user)
        list_response = self.client.get(reverse("reproductionrecord-list"))
        self.assertEqual(list_response.status_code, 200)
        self.assertTrue(len(list_response.json()) >= 1)

        detail_response = self.client.get(reverse("reproductionrecord-detail", args=[self.record.pk]))
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["event_type"], self.record.event_type)

    def test_api_003_valid_reproduction_create(self):
        self.client.force_login(self.user)
        payload = {
            "target": self.herd.pk,
            "event_date": "2026-09-13",
            "event_type": "mổ",
            "result": "thành công",
            "notes": "Ghi chú",
        }
        response = self.client.post(reverse("reproductionrecord-list"), payload, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(ReproductionRecord.objects.filter(event_type="mổ").exists())

    def test_api_004_invalid_reproduction_create_missing_event_type(self):
        self.client.force_login(self.user)
        payload = {
            "target": self.herd.pk,
            "event_date": "2026-09-13",
            "event_type": "",
            "result": "thành công",
            "notes": "Sai",
        }
        response = self.client.post(reverse("reproductionrecord-list"), payload, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_api_005_reproduction_update_and_delete(self):
        self.client.force_login(self.user)
        update_response = self.client.patch(
            reverse("reproductionrecord-detail", args=[self.record.pk]),
            {"event_type": "đẻ lại"},
            content_type="application/json",
        )
        self.assertEqual(update_response.status_code, 200)

        delete_response = self.client.delete(reverse("reproductionrecord-detail", args=[self.record.pk]))
        self.assertEqual(delete_response.status_code, 204)

    def test_api_006_invalid_herd_reference(self):
        self.client.force_login(self.user)
        payload = {
            "target": 999999,
            "event_date": "2026-09-13",
            "event_type": "đẻ",
            "result": "thành công",
        }
        response = self.client.post(reverse("reproductionrecord-list"), payload, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_api_007_missing_object_returns_404(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("reproductionrecord-detail", args=[999999]))
        self.assertEqual(response.status_code, 404)
