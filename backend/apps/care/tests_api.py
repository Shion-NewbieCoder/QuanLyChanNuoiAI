from datetime import datetime, timezone
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from apps.herds.models import Herd

from .models import CareLog, FeedRecord, MedicineRecord


class CareApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="care-manager",
            password="secretpass123",
        )
        cls.user.groups.add(Group.objects.get(name="quản lý"))
        cls.herd = Herd.objects.create(
            code="HERD-001",
            name="Đàn bò sữa",
            animal_type="bò",
            management_mode="group",
            quantity=10,
            status="active",
        )
        cls.recorded_at = datetime(2026, 9, 7, 8, 30, tzinfo=timezone.utc)
        cls.care_log = CareLog.objects.create(
            herd=cls.herd,
            recorded_at=cls.recorded_at,
            activity="Vệ sinh chuồng",
            notes="Hoàn thành",
        )
        cls.feed_record = FeedRecord.objects.create(
            herd=cls.herd,
            recorded_at=cls.recorded_at,
            feed_type="Cỏ tươi",
            quantity=Decimal("12.50"),
            notes="Buổi sáng",
        )
        cls.medicine_record = MedicineRecord.objects.create(
            herd=cls.herd,
            recorded_at=cls.recorded_at,
            medicine="Vitamin",
            dose=Decimal("2.50"),
            notes="Theo dõi",
        )

    def test_api_001_care_unauthenticated_list_denied(self):
        response = self.client.get(reverse("carelog-list"))
        self.assertIn(response.status_code, (401, 403))

    def test_api_002_care_authenticated_list_succeeds(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("carelog-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) >= 1)

    def test_api_003_care_retrieve_existing(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("carelog-detail", args=[self.care_log.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["activity"], self.care_log.activity)

    def test_api_004_care_create_valid(self):
        self.client.force_login(self.user)
        payload = {
            "herd": self.herd.pk,
            "recorded_at": "2026-09-07T09:00:00Z",
            "activity": "Cho ăn",
            "notes": "Bữa trưa",
        }
        response = self.client.post(reverse("carelog-list"), payload, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(CareLog.objects.filter(activity="Cho ăn").exists())

    def test_api_005_care_create_invalid_missing_herd(self):
        self.client.force_login(self.user)
        payload = {
            "herd": 999999,
            "recorded_at": "2026-09-07T09:00:00Z",
            "activity": "Cho ăn",
            "notes": "Bữa trưa",
        }
        response = self.client.post(reverse("carelog-list"), payload, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_api_006_care_update_valid(self):
        self.client.force_login(self.user)
        payload = {"activity": "Vệ sinh chuồng mới", "notes": "Xong"}
        response = self.client.patch(
            reverse("carelog-detail", args=[self.care_log.pk]),
            payload,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.care_log.refresh_from_db()
        self.assertEqual(self.care_log.activity, "Vệ sinh chuồng mới")

    def test_api_007_care_update_invalid_missing_herd(self):
        self.client.force_login(self.user)
        payload = {"herd": 999999}
        response = self.client.patch(
            reverse("carelog-detail", args=[self.care_log.pk]),
            payload,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_api_008_care_delete(self):
        self.client.force_login(self.user)
        response = self.client.delete(reverse("carelog-detail", args=[self.care_log.pk]))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(CareLog.objects.filter(pk=self.care_log.pk).exists())

    def test_api_009_feed_list_and_create(self):
        self.client.force_login(self.user)
        list_response = self.client.get(reverse("feedrecord-list"))
        self.assertEqual(list_response.status_code, 200)

        payload = {
            "herd": self.herd.pk,
            "recorded_at": "2026-09-07T10:00:00Z",
            "feed_type": "Thức ăn hỗn hợp",
            "quantity": "8.25",
            "notes": "Buổi chiều",
        }
        create_response = self.client.post(reverse("feedrecord-list"), payload, content_type="application/json")
        self.assertEqual(create_response.status_code, 201)

    def test_api_010_feed_invalid_negative_quantity(self):
        self.client.force_login(self.user)
        payload = {
            "herd": self.herd.pk,
            "recorded_at": "2026-09-07T10:00:00Z",
            "feed_type": "Thức ăn hỗn hợp",
            "quantity": "-1",
            "notes": "Sai",
        }
        response = self.client.post(reverse("feedrecord-list"), payload, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_api_011_feed_update_and_delete(self):
        self.client.force_login(self.user)
        update_response = self.client.patch(
            reverse("feedrecord-detail", args=[self.feed_record.pk]),
            {"feed_type": "Cỏ xanh"},
            content_type="application/json",
        )
        self.assertEqual(update_response.status_code, 200)

        delete_response = self.client.delete(reverse("feedrecord-detail", args=[self.feed_record.pk]))
        self.assertEqual(delete_response.status_code, 204)

    def test_api_012_medicine_list_and_create(self):
        self.client.force_login(self.user)
        list_response = self.client.get(reverse("medicinerecord-list"))
        self.assertEqual(list_response.status_code, 200)

        payload = {
            "herd": self.herd.pk,
            "recorded_at": "2026-09-07T11:00:00Z",
            "medicine": "Vitamin C",
            "dose": "3.00",
            "notes": "Uống thuốc",
        }
        create_response = self.client.post(reverse("medicinerecord-list"), payload, content_type="application/json")
        self.assertEqual(create_response.status_code, 201)

    def test_api_013_medicine_invalid_negative_dose(self):
        self.client.force_login(self.user)
        payload = {
            "herd": self.herd.pk,
            "recorded_at": "2026-09-07T11:00:00Z",
            "medicine": "Vitamin C",
            "dose": "-2",
            "notes": "Sai",
        }
        response = self.client.post(reverse("medicinerecord-list"), payload, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_api_014_medicine_update_and_delete(self):
        self.client.force_login(self.user)
        update_response = self.client.patch(
            reverse("medicinerecord-detail", args=[self.medicine_record.pk]),
            {"medicine": "Vitamin D"},
            content_type="application/json",
        )
        self.assertEqual(update_response.status_code, 200)

        delete_response = self.client.delete(reverse("medicinerecord-detail", args=[self.medicine_record.pk]))
        self.assertEqual(delete_response.status_code, 204)

    def test_api_015_missing_object_returns_404(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("carelog-detail", args=[999999])).status_code, 404)
        self.assertEqual(self.client.get(reverse("feedrecord-detail", args=[999999])).status_code, 404)
        self.assertEqual(self.client.get(reverse("medicinerecord-detail", args=[999999])).status_code, 404)

    def test_api_016_permission_requires_authentication(self):
        self.assertIn(self.client.get(reverse("carelog-list")).status_code, (401, 403))
        self.assertIn(self.client.get(reverse("feedrecord-list")).status_code, (401, 403))
        self.assertIn(self.client.get(reverse("medicinerecord-list")).status_code, (401, 403))

        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("carelog-list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("feedrecord-list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("medicinerecord-list")).status_code, 200)
