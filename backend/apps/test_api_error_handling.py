from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from rest_framework.permissions import AllowAny
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from apps.herds.models import Herd


class ExplodingApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        raise RuntimeError("internal diagnostic must not reach the client")


class ApiErrorHandlingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="error-contract-user",
            password="secretpass123",
        )
        cls.user.groups.add(Group.objects.get(name="quản lý"))
        cls.herd = Herd.objects.create(
            code="HERD-ERROR-001",
            name="Error contract herd",
            animal_type="cattle",
            management_mode="group",
            quantity=10,
            status="active",
        )

    def test_error_001_validation_error_uses_structured_400_contract(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("herd-list"),
            {
                "code": "HERD-ERROR-002",
                "name": "Invalid herd",
                "animal_type": "cattle",
                "management_mode": "group",
                "quantity": -1,
                "status": "active",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error_code"], "validation_error")
        self.assertEqual(response.json()["message"], "Validation failed.")
        self.assertIn("quantity", response.json()["field_errors"])

    def test_error_002_invalid_reference_uses_structured_400_contract(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("animal-list"),
            {"code": "ANIMAL-ERROR", "herd": 999999, "status": "active"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error_code"], "validation_error")
        self.assertIn("herd", response.json()["field_errors"])

    def test_error_003_unauthenticated_api_request_uses_safe_contract(self):
        response = self.client.get(reverse("herd-list"))
        self.assertIn(response.status_code, (401, 403))
        self.assertEqual(response.json()["error_code"], "authentication_required")
        self.assertNotIn("field_errors", response.json())

    def test_error_004_missing_resource_uses_safe_404_contract(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("herd-detail", args=[999999]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error_code": "not_found", "message": "Resource not found."})

    def test_error_005_unexpected_exception_is_safe_and_logged(self):
        request = APIRequestFactory().get("/api/test-exception")
        with self.assertLogs("config.api_exceptions", level="ERROR") as logs:
            response = ExplodingApiView.as_view()(request)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.data,
            {
                "error_code": "internal_error",
                "message": "An unexpected server error occurred.",
            },
        )
        self.assertNotIn("internal diagnostic", str(response.data))
        self.assertIn("Unexpected API exception", "\n".join(logs.output))

    def test_error_006_successful_api_response_is_unchanged(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("herd-detail", args=[self.herd.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], self.herd.code)
        self.assertNotIn("error_code", response.json())
