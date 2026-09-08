from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase

from apps.herds.models import Animal, AnimalGroup, Herd
from .templatetags.farm_visuals import farm_avatar


class AvatarSelectionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = get_user_model().objects.create_user(username="avatar-manager")
        cls.manager.groups.add(Group.objects.get(name="quản lý"))
        cls.employee = get_user_model().objects.create_user(username="avatar-employee")
        cls.employee.groups.add(Group.objects.get(name="nhân viên"))
        cls.herd = Herd.objects.create(code="AV-H", name="Đàn", animal_type="bò", management_mode="group", quantity=4, status="active")
        cls.payloads = {
            "herds": (Herd, dict(code="NEW", name="Đàn mới", animal_type="bò", management_mode="group", quantity=2, status="active")),
            "animals": (Animal, dict(code="NEW", herd=cls.herd.pk, status="active")),
            "animal-groups": (AnimalGroup, dict(code="NEW", name="Nhóm mới", herd=cls.herd.pk, quantity=2, status="active")),
        }

    def setUp(self):
        self.client.force_login(self.manager)

    def test_picker_and_selection_persist_for_each_resource(self):
        for slug, (model, payload) in self.payloads.items():
            with self.subTest(slug=slug):
                page = self.client.get(f"/{slug}/create/")
                self.assertContains(page, 'type="radio"', count=8)
                self.assertContains(page, 'value="cow"')
                response = self.client.post(f"/{slug}/create/", {**payload, "avatar": "goat"})
                self.assertEqual(response.status_code, 302)
                obj = model.objects.get(code="NEW")
                self.assertEqual(obj.avatar, "goat")
                # A separate browser session reads the saved preference too.
                other_client = Client()
                other_client.force_login(self.manager)
                self.assertContains(other_client.get(response.url), '/static/images/farm/goat.svg')
                edit = self.client.get(response.url + "edit/")
                self.assertEqual(edit.context["form"]["avatar"].value(), "goat")
                self.assertContains(self.client.get(f"/{slug}/"), '/static/images/farm/goat.svg')

    def test_change_selection_and_return_to_automatic(self):
        self.herd.avatar = "pig"
        self.herd.save()
        url = f"/herds/{self.herd.pk}/edit/"
        payload = self.payloads["herds"][1]
        self.assertEqual(self.client.post(url, {**payload, "avatar": "sheep"}).status_code, 302)
        self.herd.refresh_from_db()
        self.assertEqual(farm_avatar(self.herd), "images/farm/sheep.svg")
        self.assertEqual(self.client.post(url, {**payload, "avatar": ""}).status_code, 302)
        self.herd.refresh_from_db()
        self.assertEqual(self.herd.avatar, "")
        self.assertEqual(farm_avatar(self.herd), "images/farm/cow.svg")

    def test_invalid_avatar_rejected_without_saving(self):
        for value in ("../../secret", "https://example.com/photo.png", '<script>alert(1)</script>'):
            response = self.client.post("/animals/create/", {**self.payloads["animals"][1], "avatar": value})
            self.assertEqual(response.status_code, 200)
            self.assertIn("avatar", response.context["form"].errors)
        self.assertFalse(Animal.objects.filter(code="NEW").exists())

    def test_invalid_business_input_keeps_selected_avatar_without_mutation(self):
        response = self.client.post(f"/herds/{self.herd.pk}/edit/", {**self.payloads["herds"][1], "quantity": -1, "avatar": "buffalo"})
        self.assertEqual(response.context["form"]["avatar"].value(), "buffalo")
        self.assertIn("quantity", response.context["form"].errors)
        self.herd.refresh_from_db()
        self.assertEqual(self.herd.avatar, "")

    def test_permissions_and_csrf_cover_avatar_updates(self):
        self.client.force_login(self.employee)
        url = f"/herds/{self.herd.pk}/edit/"
        self.assertEqual(self.client.post(url, {**self.payloads["herds"][1], "avatar": "pig"}).status_code, 403)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.manager)
        self.assertEqual(csrf_client.post(url, {**self.payloads["herds"][1], "avatar": "pig"}).status_code, 403)
        self.herd.refresh_from_db()
        self.assertEqual(self.herd.avatar, "")

    def test_existing_api_updates_preserve_ui_preference(self):
        self.herd.avatar = "herd"
        self.herd.save()
        response = self.client.patch(f"/api/herds/{self.herd.pk}/", {"name": "Đổi tên"}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("avatar", response.json())
        self.herd.refresh_from_db()
        self.assertEqual(self.herd.avatar, "herd")
