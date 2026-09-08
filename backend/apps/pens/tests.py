from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.herds.models import Animal, AnimalGroup, Herd

from .models import Pen


class PenModelTests(TestCase):
    def setUp(self):
        self.herd = Herd.objects.create(
            code="HERD-001",
            name="Đàn bò sữa",
            animal_type="bò",
            management_mode="group",
            quantity=10,
            status="active",
        )
        self.animal_group = AnimalGroup.objects.create(
            code="GROUP-001",
            name="Nhóm bò cái",
            herd=self.herd,
            quantity=5,
            status="active",
        )
        self.animal = Animal.objects.create(
            code="ANIMAL-001",
            herd=self.herd,
            status="active",
        )

    def valid_pen_data(self, **overrides):
        data = {
            "code": "PEN-001",
            "name": "Chuồng số 1",
            "location": "Khu A",
            "description": "Chuồng chính",
            "status": "active",
            "herd": self.herd,
            "animal_group": None,
            "animal": None,
        }
        data.update(overrides)
        return data

    def test_pen_001_valid_herd_target(self):
        pen = Pen(**self.valid_pen_data())

        pen.full_clean()
        pen.save()
        self.assertEqual(Pen.objects.get(pk=pen.pk).herd_id, self.herd.pk)

    def test_pen_002_valid_animal_group_target(self):
        pen = Pen(**self.valid_pen_data(animal_group=self.animal_group, herd=None, animal=None))

        pen.full_clean()
        pen.save()
        self.assertEqual(Pen.objects.get(pk=pen.pk).animal_group_id, self.animal_group.pk)

    def test_pen_003_valid_animal_target(self):
        pen = Pen(**self.valid_pen_data(animal=self.animal, herd=None, animal_group=None))

        pen.full_clean()
        pen.save()
        self.assertEqual(Pen.objects.get(pk=pen.pk).animal_id, self.animal.pk)

    def test_pen_004_no_target_invalid(self):
        data = self.valid_pen_data(herd=None, animal_group=None, animal=None)

        with self.assertRaises(ValidationError):
            Pen(**data).full_clean()

    def test_pen_005_two_targets_invalid(self):
        data = self.valid_pen_data(herd=self.herd, animal_group=self.animal_group, animal=None)

        with self.assertRaises(ValidationError):
            Pen(**data).full_clean()

    def test_pen_006_all_three_targets_invalid(self):
        data = self.valid_pen_data(
            herd=self.herd,
            animal_group=self.animal_group,
            animal=self.animal,
        )

        with self.assertRaises(ValidationError):
            Pen(**data).full_clean()
