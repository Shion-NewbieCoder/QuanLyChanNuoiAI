from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Animal, AnimalGroup, Herd


class HerdModelTests(TestCase):
    def valid_herd_data(self):
        return {
            "code": "HERD-001",
            "name": "Đàn bò sữa",
            "animal_type": "bò",
            "management_mode": "group",
            "quantity": 10,
            "status": "active",
        }

    def test_herd_001_valid_herd(self):
        herd = Herd(**self.valid_herd_data())
        herd.full_clean()
        herd.save()
        self.assertEqual(Herd.objects.get(pk=herd.pk).code, "HERD-001")

    def test_herd_002_missing_required_field_fails_validation(self):
        data = self.valid_herd_data()
        data["name"] = ""

        with self.assertRaises(ValidationError):
            Herd(**data).full_clean()

    def test_herd_003_negative_quantity_fails_validation(self):
        data = self.valid_herd_data()
        data["quantity"] = -1

        with self.assertRaises(ValidationError):
            Herd(**data).full_clean()

    def test_animal_001_valid_herd_reference(self):
        herd = Herd.objects.create(**self.valid_herd_data())
        animal = Animal(code="ANIMAL-001", herd=herd, status="active")

        animal.full_clean()
        animal.save()
        self.assertEqual(Animal.objects.get(pk=animal.pk).herd_id, herd.pk)

    def test_animal_002_missing_herd_reference_fails_validation(self):
        animal = Animal(code="ANIMAL-001", herd_id=999999, status="active")

        with self.assertRaises(ValidationError):
            animal.full_clean()

    def test_animal_group_001_valid_herd_reference(self):
        herd = Herd.objects.create(**self.valid_herd_data())
        group = AnimalGroup(
            code="GROUP-001",
            name="Nhóm bò sữa",
            herd=herd,
            quantity=5,
            status="active",
        )

        group.full_clean()
        group.save()
        self.assertEqual(AnimalGroup.objects.get(pk=group.pk).herd_id, herd.pk)

    def test_animal_group_002_negative_quantity_fails_validation(self):
        herd = Herd.objects.create(**self.valid_herd_data())
        group = AnimalGroup(
            code="GROUP-001",
            name="Nhóm bò sữa",
            herd=herd,
            quantity=-1,
            status="active",
        )

        with self.assertRaises(ValidationError):
            group.full_clean()

    def test_persistence_001_saved_data_can_be_read_back(self):
        herd = Herd.objects.create(**self.valid_herd_data())
        group = AnimalGroup.objects.create(
            code="GROUP-001",
            name="Nhóm bò sữa",
            herd=herd,
            quantity=5,
            status="active",
        )

        loaded = AnimalGroup.objects.get(pk=group.pk)

        self.assertEqual(loaded.code, group.code)
        self.assertEqual(loaded.name, group.name)
        self.assertEqual(loaded.quantity, group.quantity)
        self.assertEqual(loaded.herd_id, herd.pk)
