from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from apps.care.models import CareLog
from apps.growth.models import GrowthRecord
from apps.herds.models import Herd
from apps.reproduction.models import ReproductionRecord
from apps.sales.models import SaleRecord
from apps.vaccinations.models import VaccineSchedule
from apps.users.permissions import ROLE_ACTIONS, RoleActionPermission
from apps.users.roles import (
    ROLE_EMPLOYEE,
    ROLE_MANAGEMENT,
    ROLE_TECHNICIAN,
    get_user_role,
)


class RoleResolutionTests(TestCase):
    def make_user(self, *roles):
        user = get_user_model().objects.create_user(username="-".join(roles) or "no-role")
        user.groups.add(*Group.objects.filter(name__in=roles))
        return user

    def test_effective_role_uses_documented_precedence(self):
        cases = (
            ((ROLE_MANAGEMENT,), ROLE_MANAGEMENT),
            ((ROLE_TECHNICIAN,), ROLE_TECHNICIAN),
            ((ROLE_EMPLOYEE,), ROLE_EMPLOYEE),
            ((ROLE_MANAGEMENT, ROLE_TECHNICIAN), ROLE_MANAGEMENT),
            ((ROLE_MANAGEMENT, ROLE_EMPLOYEE), ROLE_MANAGEMENT),
            ((ROLE_TECHNICIAN, ROLE_EMPLOYEE), ROLE_TECHNICIAN),
            ((ROLE_MANAGEMENT, ROLE_TECHNICIAN, ROLE_EMPLOYEE), ROLE_MANAGEMENT),
        )
        for roles, expected in cases:
            with self.subTest(roles=roles):
                self.assertEqual(get_user_role(self.make_user(*roles)), expected)

    def test_no_recognized_role_returns_none(self):
        self.assertIsNone(get_user_role(self.make_user()))


class RoleActionPermissionTests(TestCase):
    factory = APIRequestFactory()

    def setUp(self):
        self.users = {}
        for role in (ROLE_MANAGEMENT, ROLE_TECHNICIAN, ROLE_EMPLOYEE):
            user = get_user_model().objects.create_user(username=role)
            user.groups.add(Group.objects.get(name=role))
            self.users[role] = user

    def allows(self, role, resource, action):
        request = self.factory.get("/")
        request.user = self.users[role]
        view = SimpleNamespace(action=action, permission_resource=resource)
        return RoleActionPermission().has_permission(request, view)

    def test_every_approved_resource_group_matches_action_matrix(self):
        expected = {
            "master_data": {
                ROLE_MANAGEMENT: {"create", "read", "update", "delete"},
                ROLE_TECHNICIAN: {"read"}, ROLE_EMPLOYEE: {"read"},
            },
            "care": {
                ROLE_MANAGEMENT: {"create", "read", "update", "delete"},
                ROLE_TECHNICIAN: {"create", "read", "update"},
                ROLE_EMPLOYEE: {"create", "read"},
            },
            "vaccination": {
                ROLE_MANAGEMENT: {"create", "read", "update", "delete"},
                ROLE_TECHNICIAN: {"create", "read", "update"},
                ROLE_EMPLOYEE: {"read"},
            },
            "growth_reproduction": {
                ROLE_MANAGEMENT: {"create", "read", "update", "delete"},
                ROLE_TECHNICIAN: {"create", "read", "update"},
                ROLE_EMPLOYEE: {"read"},
            },
            "sales": {
                ROLE_MANAGEMENT: {"create", "read", "update", "delete"},
                ROLE_TECHNICIAN: {"read"}, ROLE_EMPLOYEE: {"read"},
            },
            "statistics": {
                ROLE_MANAGEMENT: {"read"}, ROLE_TECHNICIAN: {"read"}, ROLE_EMPLOYEE: set(),
            },
            "ai": {
                ROLE_MANAGEMENT: {"read"}, ROLE_TECHNICIAN: {"read"}, ROLE_EMPLOYEE: set(),
            },
        }
        self.assertEqual(ROLE_ACTIONS, expected)
        action_to_drf = {"create": "create", "read": "list", "update": "partial_update", "delete": "destroy"}
        for resource, roles in expected.items():
            for role, allowed in roles.items():
                for action, drf_action in action_to_drf.items():
                    with self.subTest(resource=resource, role=role, action=action):
                        self.assertEqual(self.allows(role, resource, drf_action), action in allowed)


class RoleApiSecurityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = {}
        for role in (ROLE_MANAGEMENT, ROLE_TECHNICIAN, ROLE_EMPLOYEE):
            user = get_user_model().objects.create_user(username=f"api-{role}")
            user.groups.add(Group.objects.get(name=role))
            cls.users[role] = user
        cls.no_role = get_user_model().objects.create_user(username="api-no-role")
        cls.herd = Herd.objects.create(code="SEC-HERD", name="Security herd", animal_type="cattle", management_mode="group", quantity=10, status="active")
        cls.care = CareLog.objects.create(herd=cls.herd, recorded_at="2026-01-01T00:00:00Z", activity="care")
        cls.schedule = VaccineSchedule.objects.create(target=cls.herd, vaccine="vaccine", scheduled_date="2026-02-01")
        cls.growth = GrowthRecord.objects.create(target=cls.herd, measurement_date="2026-01-01", weight="10.00")
        cls.reproduction = ReproductionRecord.objects.create(target=cls.herd, event_date="2026-01-01", event_type="event")
        cls.sale = SaleRecord.objects.create(target=cls.herd, sale_date="2026-01-01", amount="100.00")

    def request_as(self, role, method, url, payload=None):
        self.client.force_login(self.users[role])
        response = getattr(self.client, method)(url, payload, content_type="application/json") if payload is not None else getattr(self.client, method)(url)
        self.client.logout()
        return response

    def test_master_data_manager_crud_and_non_managers_read_only(self):
        list_url = reverse("herd-list")
        detail_url = reverse("herd-detail", args=[self.herd.pk])
        payload = {"code": "SEC-HERD-2", "name": "Second", "animal_type": "cattle", "management_mode": "group", "quantity": 1, "status": "active"}
        self.assertEqual(self.request_as(ROLE_MANAGEMENT, "post", list_url, payload).status_code, 201)
        for role in (ROLE_TECHNICIAN, ROLE_EMPLOYEE):
            self.assertEqual(self.request_as(role, "get", list_url).status_code, 200)
            self.assertEqual(self.request_as(role, "post", list_url, payload).status_code, 403)
            self.assertEqual(self.request_as(role, "patch", detail_url, {"quantity": 2}).status_code, 403)
            self.assertEqual(self.request_as(role, "delete", detail_url).status_code, 403)

    def test_care_policy_and_permission_error_envelope(self):
        list_url = reverse("carelog-list")
        detail_url = reverse("carelog-detail", args=[self.care.pk])
        payload = {"herd": self.herd.pk, "recorded_at": "2026-01-02T00:00:00Z", "activity": "new care"}
        self.assertEqual(self.request_as(ROLE_TECHNICIAN, "post", list_url, payload).status_code, 201)
        self.assertEqual(self.request_as(ROLE_TECHNICIAN, "patch", detail_url, {"activity": "updated"}).status_code, 200)
        denied = self.request_as(ROLE_TECHNICIAN, "delete", detail_url)
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(denied.json()["error_code"], "permission_denied")
        self.assertEqual(self.request_as(ROLE_EMPLOYEE, "post", list_url, payload).status_code, 201)
        self.assertEqual(self.request_as(ROLE_EMPLOYEE, "patch", detail_url, {"activity": "blocked"}).status_code, 403)

    def test_vaccination_growth_reproduction_and_sales_groups(self):
        cases = (
            ("vaccineschedule-list", "vaccineschedule-detail", self.schedule.pk, {"target": self.herd.pk, "vaccine": "new", "scheduled_date": "2026-02-02"}),
            ("growthrecord-list", "growthrecord-detail", self.growth.pk, {"target": self.herd.pk, "measurement_date": "2026-02-02", "weight": "11.00"}),
            ("reproductionrecord-list", "reproductionrecord-detail", self.reproduction.pk, {"target": self.herd.pk, "event_date": "2026-02-02", "event_type": "new"}),
        )
        for list_name, detail_name, pk, payload in cases:
            with self.subTest(resource=list_name):
                self.assertEqual(self.request_as(ROLE_TECHNICIAN, "post", reverse(list_name), payload).status_code, 201)
                self.assertEqual(self.request_as(ROLE_TECHNICIAN, "patch", reverse(detail_name, args=[pk]), payload).status_code, 200)
                self.assertEqual(self.request_as(ROLE_TECHNICIAN, "delete", reverse(detail_name, args=[pk])).status_code, 403)
                self.assertEqual(self.request_as(ROLE_EMPLOYEE, "get", reverse(list_name)).status_code, 200)
                self.assertEqual(self.request_as(ROLE_EMPLOYEE, "post", reverse(list_name), payload).status_code, 403)
        sale_url = reverse("salerecord-list")
        sale_payload = {"target": self.herd.pk, "sale_date": "2026-02-02", "amount": "20.00"}
        for role in (ROLE_TECHNICIAN, ROLE_EMPLOYEE):
            self.assertEqual(self.request_as(role, "get", sale_url).status_code, 200)
            self.assertEqual(self.request_as(role, "post", sale_url, sale_payload).status_code, 403)

    def test_statistics_no_role_and_unauthenticated_are_denied(self):
        for role in (ROLE_MANAGEMENT, ROLE_TECHNICIAN):
            self.assertEqual(self.request_as(role, "get", reverse("statistics-growth")).status_code, 200)
        self.assertEqual(self.request_as(ROLE_EMPLOYEE, "get", reverse("statistics-growth")).status_code, 403)
        self.client.force_login(self.no_role)
        denied = self.client.get(reverse("herd-list"))
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(denied.json()["error_code"], "permission_denied")
        self.client.logout()
        self.assertIn(self.client.get(reverse("herd-list")).status_code, (401, 403))
