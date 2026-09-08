from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from .models import Animal, AnimalGroup, Herd


class HerdApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="herd-manager",
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

    def test_api_001_unauthenticated_list_is_denied(self):
        response = self.client.get(reverse("herd-list"))
        self.assertIn(response.status_code, (401, 403))

    def test_api_002_authenticated_list_succeeds(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("herd-list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) >= 1)

    def test_api_003_retrieve_existing_herd(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("herd-detail", args=[self.herd.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], self.herd.code)

    def test_api_004_create_valid_herd(self):
        self.client.force_login(self.user)
        payload = {
            "code": "HERD-002",
            "name": "Đàn cừu",
            "animal_type": "cừu",
            "management_mode": "group",
            "quantity": 5,
            "status": "active",
        }

        response = self.client.post(reverse("herd-list"), payload, content_type="application/json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Herd.objects.filter(code="HERD-002").count(), 1)

    def test_api_005_create_invalid_herd_fails(self):
        self.client.force_login(self.user)
        payload = {
            "code": "HERD-003",
            "name": "Đàn cừu",
            "animal_type": "cừu",
            "management_mode": "group",
            "quantity": -1,
            "status": "active",
        }

        response = self.client.post(reverse("herd-list"), payload, content_type="application/json")

        self.assertEqual(response.status_code, 400)

    def test_api_006_update_valid_herd(self):
        self.client.force_login(self.user)
        payload = {"name": "Đàn bò sữa mới", "quantity": 12}

        response = self.client.patch(
            reverse("herd-detail", args=[self.herd.pk]),
            payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.herd.refresh_from_db()
        self.assertEqual(self.herd.name, "Đàn bò sữa mới")
        self.assertEqual(self.herd.quantity, 12)

    def test_api_007_update_invalid_herd_fails(self):
        self.client.force_login(self.user)
        payload = {"quantity": -10}

        response = self.client.patch(
            reverse("herd-detail", args=[self.herd.pk]),
            payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_api_008_delete_herd(self):
        self.client.force_login(self.user)

        response = self.client.delete(reverse("herd-detail", args=[self.herd.pk]))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Herd.objects.filter(pk=self.herd.pk).exists())

    def test_api_009_permission_requires_authentication(self):
        response = self.client.get(reverse("herd-list"))
        self.assertIn(response.status_code, (401, 403))

        self.client.force_login(self.user)
        response = self.client.get(reverse("herd-list"))
        self.assertEqual(response.status_code, 200)


class AnimalApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="animal-manager",
            password="secretpass123",
        )
        cls.user.groups.add(Group.objects.get(name="quản lý"))
        cls.herd = Herd.objects.create(
            code="HERD-ANIMAL-001",
            name="Animal herd",
            animal_type="cattle",
            management_mode="group",
            quantity=10,
            status="active",
        )
        cls.animal = Animal.objects.create(
            code="ANIMAL-001",
            herd=cls.herd,
            status="active",
        )

    def test_animal_001_unauthenticated_list_is_denied(self):
        response = self.client.get(reverse("animal-list"))
        self.assertIn(response.status_code, (401, 403))

    def test_animal_002_authenticated_list_succeeds(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("animal-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) >= 1)

    def test_animal_003_retrieve_existing_animal(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("animal-detail", args=[self.animal.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], self.animal.code)

    def test_animal_004_create_valid_animal(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("animal-list"),
            {"code": "ANIMAL-002", "herd": self.herd.pk, "status": "active"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Animal.objects.filter(code="ANIMAL-002").exists())

    def test_animal_005_invalid_create_fails(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("animal-list"),
            {"herd": self.herd.pk, "status": "active"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_animal_006_valid_update(self):
        self.client.force_login(self.user)
        response = self.client.patch(
            reverse("animal-detail", args=[self.animal.pk]),
            {"status": "inactive"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.animal.refresh_from_db()
        self.assertEqual(self.animal.status, "inactive")

    def test_animal_007_invalid_update_fails(self):
        self.client.force_login(self.user)
        response = self.client.patch(
            reverse("animal-detail", args=[self.animal.pk]),
            {"herd": 999999},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_animal_008_delete(self):
        self.client.force_login(self.user)
        response = self.client.delete(reverse("animal-detail", args=[self.animal.pk]))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Animal.objects.filter(pk=self.animal.pk).exists())

    def test_animal_009_invalid_herd_reference_fails(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("animal-list"),
            {"code": "ANIMAL-003", "herd": 999999, "status": "active"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


class AnimalGroupApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="animal-group-manager",
            password="secretpass123",
        )
        cls.user.groups.add(Group.objects.get(name="quản lý"))
        cls.herd = Herd.objects.create(
            code="HERD-GROUP-001",
            name="Animal group herd",
            animal_type="cattle",
            management_mode="group",
            quantity=10,
            status="active",
        )
        cls.group = AnimalGroup.objects.create(
            code="GROUP-001",
            name="Group one",
            herd=cls.herd,
            quantity=5,
            status="active",
        )

    def test_animal_group_001_unauthenticated_list_is_denied(self):
        response = self.client.get(reverse("animalgroup-list"))
        self.assertIn(response.status_code, (401, 403))

    def test_animal_group_002_authenticated_list_succeeds(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("animalgroup-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) >= 1)

    def test_animal_group_003_retrieve_existing_group(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("animalgroup-detail", args=[self.group.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], self.group.code)

    def test_animal_group_004_create_valid_group(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("animalgroup-list"),
            {
                "code": "GROUP-002",
                "name": "Group two",
                "herd": self.herd.pk,
                "quantity": 4,
                "status": "active",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(AnimalGroup.objects.filter(code="GROUP-002").exists())

    def test_animal_group_005_invalid_create_fails(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("animalgroup-list"),
            {
                "code": "GROUP-003",
                "name": "Invalid group",
                "herd": self.herd.pk,
                "quantity": -1,
                "status": "active",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_animal_group_006_valid_update(self):
        self.client.force_login(self.user)
        response = self.client.patch(
            reverse("animalgroup-detail", args=[self.group.pk]),
            {"quantity": 6},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.group.refresh_from_db()
        self.assertEqual(self.group.quantity, 6)

    def test_animal_group_007_invalid_update_fails(self):
        self.client.force_login(self.user)
        response = self.client.patch(
            reverse("animalgroup-detail", args=[self.group.pk]),
            {"quantity": -1},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_animal_group_008_delete(self):
        self.client.force_login(self.user)
        response = self.client.delete(reverse("animalgroup-detail", args=[self.group.pk]))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(AnimalGroup.objects.filter(pk=self.group.pk).exists())

    def test_animal_group_009_invalid_herd_reference_fails(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("animalgroup-list"),
            {
                "code": "GROUP-004",
                "name": "Missing herd",
                "herd": 999999,
                "quantity": 1,
                "status": "active",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
