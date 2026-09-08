from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from apps.herds.models import Herd

from .models import VaccinationRecord, VaccineSchedule


class VaccinationApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="vaccine-manager",
            password="secretpass123",
        )
        cls.user.groups.add(Group.objects.get(name="quản lý"))
        cls.herd = Herd.objects.create(
            code="HERD-VAL",
            name="Đàn gia súc",
            animal_type="bò",
            management_mode="group",
            quantity=12,
            status="active",
        )
        cls.schedule = VaccineSchedule.objects.create(
            target=cls.herd,
            vaccine="Vắc xin viêm da",
            scheduled_date=date.today() + timedelta(days=3),
            status=VaccineSchedule.Status.SCHEDULED,
        )
        cls.record = VaccinationRecord.objects.create(
            schedule=cls.schedule,
            actual_date=date.today(),
            notes="Đã tiêm",
        )

    def test_api_001_unauthenticated_denied(self):
        self.assertIn(self.client.get(reverse("vaccineschedule-list")).status_code, (401, 403))
        self.assertIn(self.client.get(reverse("vaccinationrecord-list")).status_code, (401, 403))

    def test_api_002_schedule_list_and_retrieve(self):
        self.client.force_login(self.user)
        list_response = self.client.get(reverse("vaccineschedule-list"))
        self.assertEqual(list_response.status_code, 200)
        self.assertTrue(len(list_response.json()) >= 1)

        detail_response = self.client.get(reverse("vaccineschedule-detail", args=[self.schedule.pk]))
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["vaccine"], self.schedule.vaccine)

    def test_api_003_schedule_create_valid(self):
        self.client.force_login(self.user)
        payload = {
            "target": self.herd.pk,
            "vaccine": "Vắc xin dại",
            "scheduled_date": "2026-12-15",
            "status": VaccineSchedule.Status.SCHEDULED,
        }
        response = self.client.post(reverse("vaccineschedule-list"), payload, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(VaccineSchedule.objects.filter(vaccine="Vắc xin dại").exists())

    def test_api_004_schedule_create_invalid(self):
        self.client.force_login(self.user)
        payload = {
            "target": 999999,
            "vaccine": "Vắc xin dại",
            "scheduled_date": "2026-12-15",
            "status": VaccineSchedule.Status.SCHEDULED,
        }
        response = self.client.post(reverse("vaccineschedule-list"), payload, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_api_005_schedule_valid_update(self):
        self.client.force_login(self.user)
        payload = {"status": VaccineSchedule.Status.DUE, "vaccine": "Vắc xin cập nhật"}
        response = self.client.patch(
            reverse("vaccineschedule-detail", args=[self.schedule.pk]),
            payload,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.schedule.refresh_from_db()
        self.assertEqual(self.schedule.status, VaccineSchedule.Status.DUE)

    def test_api_006_schedule_invalid_status_fails(self):
        self.client.force_login(self.user)
        payload = {"status": "not-real"}
        response = self.client.patch(
            reverse("vaccineschedule-detail", args=[self.schedule.pk]),
            payload,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_api_007_record_list_and_retrieve(self):
        self.client.force_login(self.user)
        list_response = self.client.get(reverse("vaccinationrecord-list"))
        self.assertEqual(list_response.status_code, 200)
        self.assertTrue(len(list_response.json()) >= 1)

        detail_response = self.client.get(reverse("vaccinationrecord-detail", args=[self.record.pk]))
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["notes"], self.record.notes)

    def test_api_008_record_create_valid(self):
        self.client.force_login(self.user)
        payload = {
            "schedule": self.schedule.pk,
            "actual_date": "2026-12-15",
            "notes": "Đã tiêm lần 2",
        }
        response = self.client.post(reverse("vaccinationrecord-list"), payload, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(VaccinationRecord.objects.filter(notes="Đã tiêm lần 2").exists())

    def test_api_009_record_invalid_reference_fails(self):
        self.client.force_login(self.user)
        payload = {"schedule": 999999, "actual_date": "2026-12-15", "notes": "bad"}
        response = self.client.post(reverse("vaccinationrecord-list"), payload, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_api_010_record_update_and_delete(self):
        self.client.force_login(self.user)
        update_response = self.client.patch(
            reverse("vaccinationrecord-detail", args=[self.record.pk]),
            {"notes": "Cập nhật ghi chú"},
            content_type="application/json",
        )
        self.assertEqual(update_response.status_code, 200)

        delete_response = self.client.delete(reverse("vaccinationrecord-detail", args=[self.record.pk]))
        self.assertEqual(delete_response.status_code, 204)

    def test_api_011_alert_classification_overdue(self):
        schedule = VaccineSchedule.objects.create(
            target=self.herd,
            vaccine="Vắc xin quá hạn",
            scheduled_date=date.today() - timedelta(days=5),
            status=VaccineSchedule.Status.SCHEDULED,
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("vaccineschedule-detail", args=[schedule.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["alert_classification"], "overdue")

    def test_api_012_alert_classification_due_today_and_due_soon(self):
        today = date.today()
        due_today = VaccineSchedule.objects.create(
            target=self.herd,
            vaccine="Vắc xin hôm nay",
            scheduled_date=today,
            status=VaccineSchedule.Status.DUE,
        )
        due_soon = VaccineSchedule.objects.create(
            target=self.herd,
            vaccine="Vắc xin sắp tới",
            scheduled_date=today + timedelta(days=3),
            status=VaccineSchedule.Status.SCHEDULED,
        )

        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("vaccineschedule-detail", args=[due_today.pk])).json()["alert_classification"], "due today")
        self.assertEqual(self.client.get(reverse("vaccineschedule-detail", args=[due_soon.pk])).json()["alert_classification"], "due soon")

    def test_api_013_alert_classification_not_yet_due_and_completed(self):
        future = VaccineSchedule.objects.create(
            target=self.herd,
            vaccine="Vắc xin chưa tới hạn",
            scheduled_date=date.today() + timedelta(days=20),
            status=VaccineSchedule.Status.SCHEDULED,
        )
        completed = VaccineSchedule.objects.create(
            target=self.herd,
            vaccine="Vắc xin đã xong",
            scheduled_date=date.today(),
            status=VaccineSchedule.Status.COMPLETED,
        )

        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("vaccineschedule-detail", args=[future.pk])).json()["alert_classification"], "scheduled-not-yet-due")
        self.assertIsNone(self.client.get(reverse("vaccineschedule-detail", args=[completed.pk])).json()["alert_classification"])

    def test_api_014_permission_requires_authentication(self):
        response = self.client.get(reverse("vaccineschedule-list"))
        self.assertIn(response.status_code, (401, 403))

        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("vaccineschedule-list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("vaccinationrecord-list")).status_code, 200)
