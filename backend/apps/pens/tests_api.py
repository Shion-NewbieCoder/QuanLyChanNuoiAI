from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from apps.herds.models import Animal, AnimalGroup, Herd

from .models import Pen


class PenApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="pen-manager",
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
        cls.animal_group = AnimalGroup.objects.create(
            code="GROUP-001",
            name="Nhóm bò cái",
            herd=cls.herd,
            quantity=5,
            status="active",
        )
        cls.animal = Animal.objects.create(
            code="ANIMAL-001",
            herd=cls.herd,
            status="active",
        )
        cls.pen = Pen.objects.create(
            code="PEN-001",
            name="Chuồng số 1",
            location="Khu A",
            description="Chuồng chính",
            status="active",
            herd=cls.herd,
        )

    def test_api_001_unauthenticated_list_is_denied(self):
        response = self.client.get(reverse("pen-list"))
        self.assertIn(response.status_code, (401, 403))

    def test_api_002_authenticated_list_succeeds(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("pen-list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) >= 1)

    def test_api_003_retrieve_existing_pen(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("pen-detail", args=[self.pen.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], self.pen.code)

    def test_api_004_valid_create_with_herd_target(self):
        self.client.force_login(self.user)
        payload = {
            "code": "PEN-002",
            "name": "Chuồng số 2",
            "location": "Khu B",
            "description": "Chuồng bò",
            "status": "active",
            "herd": self.herd.pk,
            "animal_group": None,
            "animal": None,
        }

        response = self.client.post(reverse("pen-list"), payload, content_type="application/json")

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Pen.objects.filter(code="PEN-002").exists())

    def test_api_005_valid_create_with_animal_group_target(self):
        self.client.force_login(self.user)
        payload = {
            "code": "PEN-003",
            "name": "Chuồng số 3",
            "location": "Khu C",
            "description": "Chuồng nhóm",
            "status": "active",
            "herd": None,
            "animal_group": self.animal_group.pk,
            "animal": None,
        }

        response = self.client.post(reverse("pen-list"), payload, content_type="application/json")

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Pen.objects.filter(code="PEN-003").exists())

    def test_api_006_valid_create_with_animal_target(self):
        self.client.force_login(self.user)
        payload = {
            "code": "PEN-004",
            "name": "Chuồng số 4",
            "location": "Khu D",
            "description": "Chuồng cá thể",
            "status": "active",
            "herd": None,
            "animal_group": None,
            "animal": self.animal.pk,
        }

        response = self.client.post(reverse("pen-list"), payload, content_type="application/json")

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Pen.objects.filter(code="PEN-004").exists())

    def test_api_007_invalid_create_zero_targets(self):
        self.client.force_login(self.user)
        payload = {
            "code": "PEN-005",
            "name": "Chuồng không mục tiêu",
            "location": "Khu E",
            "description": "Không mục tiêu",
            "status": "active",
            "herd": None,
            "animal_group": None,
            "animal": None,
        }

        response = self.client.post(reverse("pen-list"), payload, content_type="application/json")

        self.assertEqual(response.status_code, 400)

    def test_api_008_invalid_create_two_targets(self):
        self.client.force_login(self.user)
        payload = {
            "code": "PEN-006",
            "name": "Chuồng hai mục tiêu",
            "location": "Khu F",
            "description": "Hai mục tiêu",
            "status": "active",
            "herd": self.herd.pk,
            "animal_group": self.animal_group.pk,
            "animal": None,
        }

        response = self.client.post(reverse("pen-list"), payload, content_type="application/json")

        self.assertEqual(response.status_code, 400)

    def test_api_009_invalid_create_three_targets(self):
        self.client.force_login(self.user)
        payload = {
            "code": "PEN-007",
            "name": "Chuồng ba mục tiêu",
            "location": "Khu G",
            "description": "Ba mục tiêu",
            "status": "active",
            "herd": self.herd.pk,
            "animal_group": self.animal_group.pk,
            "animal": self.animal.pk,
        }

        response = self.client.post(reverse("pen-list"), payload, content_type="application/json")

        self.assertEqual(response.status_code, 400)

    def test_api_010_valid_update(self):
        self.client.force_login(self.user)
        payload = {"name": "Chuồng số 1 mới", "status": "inactive"}

        response = self.client.patch(
            reverse("pen-detail", args=[self.pen.pk]),
            payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.pen.refresh_from_db()
        self.assertEqual(self.pen.name, "Chuồng số 1 mới")
        self.assertEqual(self.pen.status, "inactive")

    def test_api_011_invalid_update(self):
        self.client.force_login(self.user)
        payload = {"herd": self.herd.pk, "animal_group": self.animal_group.pk}

        response = self.client.patch(
            reverse("pen-detail", args=[self.pen.pk]),
            payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_api_012_delete_pen(self):
        self.client.force_login(self.user)

        response = self.client.delete(reverse("pen-detail", args=[self.pen.pk]))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Pen.objects.filter(pk=self.pen.pk).exists())

    def test_api_013_missing_object_returns_404(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("pen-detail", args=[999999]))

        self.assertEqual(response.status_code, 404)

    def test_api_014_permission_requires_authentication(self):
        response = self.client.get(reverse("pen-list"))
        self.assertIn(response.status_code, (401, 403))

        self.client.force_login(self.user)
        response = self.client.get(reverse("pen-list"))
        self.assertEqual(response.status_code, 200)
