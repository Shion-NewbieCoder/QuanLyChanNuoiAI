from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.middleware.csrf import get_token
from django.test import Client, TestCase
from django.urls import reverse

from ..roles import (
    ROLE_EMPLOYEE,
    ROLE_MANAGEMENT,
    ROLE_TECHNICIAN,
    get_user_role,
)


class AuthenticationAuthorizationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.management_user = user_model.objects.create_user(
            username="management-user",
            password="management-password",
        )
        cls.technician_user = user_model.objects.create_user(
            username="technician-user",
            password="technician-password",
        )
        cls.employee_user = user_model.objects.create_user(
            username="employee-user",
            password="employee-password",
        )

        Group.objects.get(name=ROLE_MANAGEMENT).user_set.add(cls.management_user)
        Group.objects.get(name=ROLE_TECHNICIAN).user_set.add(cls.technician_user)
        Group.objects.get(name=ROLE_EMPLOYEE).user_set.add(cls.employee_user)

    def test_auth_001_valid_credentials_create_authenticated_session(self):
        response = self.client.post(
            reverse("login"),
            {"username": "management-user", "password": "management-password"},
        )

        self.assertRedirects(response, reverse("protected-operation"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_auth_002_invalid_password_is_rejected(self):
        response = self.client.post(
            reverse("login"),
            {"username": "management-user", "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertTrue(response.context["form"].errors)

    def test_auth_003_unauthenticated_access_redirects_to_login(self):
        response = self.client.get(reverse("protected-operation"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('protected-operation')}",
        )

    def test_auth_004_role_mapping_is_exact(self):
        self.assertEqual(get_user_role(self.management_user), ROLE_MANAGEMENT)
        self.assertEqual(get_user_role(self.technician_user), ROLE_TECHNICIAN)
        self.assertEqual(get_user_role(self.employee_user), ROLE_EMPLOYEE)

    def test_auth_005_user_with_permission_can_access_protected_operation(self):
        self.client.force_login(self.management_user)

        response = self.client.get(reverse("protected-operation"))

        self.assertEqual(response.status_code, 200)

    def test_auth_006_authenticated_user_without_permission_is_rejected(self):
        self.client.force_login(self.technician_user)

        response = self.client.get(reverse("protected-operation"))

        self.assertEqual(response.status_code, 403)

    def test_auth_007_direct_request_still_enforces_server_permission(self):
        self.client.force_login(self.employee_user)

        response = self.client.get("/auth/protected/")

        self.assertEqual(response.status_code, 403)

    def test_auth_008_login_form_keeps_csrf_protection(self):
        csrf_client = Client(enforce_csrf_checks=True)
        login_url = reverse("login")
        get_response = csrf_client.get(login_url)
        csrf_token = get_token(get_response.wsgi_request)

        rejected_response = csrf_client.post(
            login_url,
            {"username": "management-user", "password": "management-password"},
        )
        accepted_response = csrf_client.post(
            login_url,
            {
                "username": "management-user",
                "password": "management-password",
                "csrfmiddlewaretoken": csrf_token,
            },
        )

        self.assertEqual(rejected_response.status_code, 403)
        self.assertEqual(accepted_response.status_code, 302)

    def test_logout_ends_session(self):
        self.client.force_login(self.management_user)

        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, reverse("login"))
        protected_response = self.client.get(reverse("protected-operation"))
        self.assertEqual(protected_response.status_code, 302)
