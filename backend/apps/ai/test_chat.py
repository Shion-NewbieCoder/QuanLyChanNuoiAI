"""Offline tests for the scoped, read-only livestock chat endpoint."""

from datetime import date
from unittest.mock import Mock, patch

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from apps.care.models import CareLog
from apps.herds.models import Animal, AnimalGroup, Herd
from apps.pens.models import Pen
from apps.users.roles import ROLE_EMPLOYEE, ROLE_MANAGEMENT, ROLE_TECHNICIAN
from apps.vaccinations.models import VaccineSchedule

from .providers import AIProviderError, AIResponse
from .openai_provider import normalize_request
from .chat import select_chat_sources


class ChatEndpointTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = {}
        for index, role in enumerate((ROLE_MANAGEMENT, ROLE_TECHNICIAN, ROLE_EMPLOYEE, None)):
            user = get_user_model().objects.create_user(username=f"chat-role-{index}")
            if role:
                user.groups.add(Group.objects.get(name=role))
            cls.users[role] = user
        cls.herd = Herd.objects.create(
            code="CHAT-001", name="Nông trại mẫu", animal_type="cattle",
            management_mode="group", quantity=14, status="active",
        )
        cls.animal = Animal.objects.create(code="AN-01", herd=cls.herd, status="active")
        cls.group = AnimalGroup.objects.create(
            code="GR-01", name="Nhóm thử", herd=cls.herd, quantity=4, status="active",
        )
        Pen.objects.create(code="PEN-01", name="Chuồng A", status="active", herd=cls.herd)
        CareLog.objects.create(
            herd=cls.herd, recorded_at="2026-06-01T08:00:00Z", activity="Vệ sinh chuồng", notes="Đã ghi nhận",
        )
        VaccineSchedule.objects.create(
            target=cls.herd, vaccine="Vaccine A", scheduled_date=date(2026, 6, 10), status="scheduled",
        )

    def setUp(self):
        self.client.force_login(self.users[ROLE_MANAGEMENT])

    def snapshot(self):
        ignored = {"auth", "users", "sessions", "contenttypes", "admin"}
        return {
            model._meta.label: list(model.objects.order_by("pk").values())
            for model in apps.get_models() if model._meta.app_label not in ignored
        }

    def post_chat(self, question, **extra):
        return self.client.post(
            "/api/ai/chat", {"question": question, **extra}, content_type="application/json",
        )

    @staticmethod
    def fake_provider(answer="Có 14 vật nuôi trong đàn CHAT-001.", error=None):
        provider = Mock(name="fake-provider")
        provider.name = "fake"
        if error:
            provider.generate.side_effect = error
        else:
            provider.generate.return_value = AIResponse(answer, "fake")
        return provider

    def test_in_scope_question_uses_only_selected_minimal_sources(self):
        provider = self.fake_provider()
        before = self.snapshot()
        with patch("apps.ai.chat.get_configured_provider", return_value=provider):
            response = self.post_chat("Đàn vật nuôi nào đang được ghi nhận?")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "Có 14 vật nuôi trong đàn CHAT-001.")
        request = provider.generate.call_args.args[0]
        self.assertEqual(request.prompt_version, "livestock-chat-v1")
        self.assertEqual(set(request.context["sources"]), {"herds"})
        self.assertEqual(request.context["sources"]["herds"], [{
            "code": "CHAT-001", "name": "Nông trại mẫu", "animal_type": "cattle",
            "management_mode": "group", "quantity": 14, "status": "active",
        }])
        self.assertNotIn("CareLog", str(request.context))
        self.assertNotIn("groups", str(request.context))
        self.assertEqual(self.snapshot(), before)

    def test_multiple_supported_sources_are_fixed_and_bounded(self):
        provider = self.fake_provider()
        with patch("apps.ai.chat.get_configured_provider", return_value=provider):
            response = self.post_chat("Cho biết đàn và chuồng nào đã ghi nhận.")
        self.assertEqual(response.status_code, 200)
        sources = provider.generate.call_args.args[0].context["sources"]
        self.assertEqual(set(sources), {"herds", "pens"})
        for value in sources.values():
            self.assertLessEqual(len(value), 10)

    def test_care_source_is_serializable_and_free_text_is_bounded(self):
        CareLog.objects.create(
            herd=self.herd, recorded_at="2026-06-02T08:00:00Z", activity="Kiểm tra",
            notes="n" * 400,
        )
        provider = self.fake_provider()
        with patch("apps.ai.chat.get_configured_provider", return_value=provider):
            response = self.post_chat("Nhật ký chăm sóc gần đây là gì?")
        self.assertEqual(response.status_code, 200)
        request = provider.generate.call_args.args[0]
        rows = request.context["sources"]["care"]
        self.assertEqual(len(rows[0]["notes"]), 240)
        self.assertTrue(rows[0]["notes_truncated"])
        self.assertIn(r'\"recorded_at\":\"2026-06-02T08:00:00+00:00\"', normalize_request(request)[1].decode())

    def test_out_of_scope_question_is_rejected_before_data_queries_and_provider(self):
        with patch("apps.ai.chat.collect_chat_facts") as collect, \
                patch("apps.ai.chat.get_configured_provider") as provider:
            response = self.post_chat("Giá vàng hôm nay bao nhiêu?")
        self.assertEqual(response.status_code, 200)
        self.assertIn("ngoài phạm vi", response.json()["answer"])
        collect.assert_not_called()
        provider.assert_not_called()

    def test_supported_business_topics_map_only_to_allowlisted_sources(self):
        expected = {
            "cá thể": "animals", "chuồng trại": "pens", "chăm sóc": "care",
            "thức ăn": "feed", "thuốc": "medicine", "vaccine": "vaccines",
            "tăng trưởng": "growth", "sinh sản": "reproduction", "xuất bán": "sales",
            "thống kê": "statistics",
        }
        for question, source in expected.items():
            with self.subTest(question=question):
                self.assertIn(source, select_chat_sources(question))
                self.assertLessEqual(len(select_chat_sources(question)), 3)

    def test_medical_advice_and_forecasting_are_rejected_before_provider(self):
        for question in (
            "Đàn này mắc bệnh gì?", "Tình trạng bệnh của đàn hiện nay?",
            "Nên dùng thuốc nào?", "Có nên tiêm vaccine cho đàn không?",
            "Dự báo tăng trưởng đàn?",
        ):
            with self.subTest(question=question), patch("apps.ai.chat.collect_chat_facts") as collect, \
                    patch("apps.ai.chat.get_configured_provider") as provider:
                response = self.post_chat(question)
            self.assertEqual(response.status_code, 200)
            collect.assert_not_called()
            provider.assert_not_called()

    def test_missing_source_data_is_reported_without_provider_call(self):
        with patch("apps.ai.chat.get_configured_provider") as provider:
            response = self.post_chat("Có những loại thức ăn nào đã ghi nhận?")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Chưa có dữ liệu đã ghi nhận về thức ăn", response.json()["answer"])
        provider.assert_not_called()

    def test_provider_failure_uses_existing_safe_api_error_contract(self):
        provider = self.fake_provider(error=AIProviderError("private provider details"))
        with patch("apps.ai.chat.get_configured_provider", return_value=provider):
            with self.assertLogs("apps.ai.orchestrator", level="WARNING"):
                response = self.post_chat("Đàn vật nuôi nào đang được ghi nhận?")
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["error_code"], "ai_provider_failure")
        self.assertNotIn("private provider details", response.content.decode())

    def test_unsafe_provider_advice_is_replaced_by_safe_refusal(self):
        provider = self.fake_provider("Nên dùng thuốc X để điều trị bệnh này.")
        with patch("apps.ai.chat.get_configured_provider", return_value=provider):
            response = self.post_chat("Đàn vật nuôi nào đang được ghi nhận?")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("thuốc X", response.json()["answer"])
        self.assertIn("ngoài phạm vi", response.json()["answer"])

    def test_ai_role_matrix_and_authentication_are_enforced_before_provider(self):
        for role in (ROLE_MANAGEMENT, ROLE_TECHNICIAN):
            self.client.force_login(self.users[role])
            provider = self.fake_provider()
            with self.subTest(role=role), patch("apps.ai.chat.get_configured_provider", return_value=provider):
                response = self.post_chat("Đàn vật nuôi nào đang được ghi nhận?")
            self.assertEqual(response.status_code, 200)
            provider.generate.assert_called_once()

        for role in (ROLE_EMPLOYEE, None):
            self.client.force_login(self.users[role])
            with self.subTest(role=role), patch("apps.ai.chat.get_configured_provider") as provider:
                response = self.post_chat("Đàn vật nuôi nào đang được ghi nhận?")
            self.assertEqual(response.status_code, 403)
            provider.assert_not_called()

        self.client.logout()
        with patch("apps.ai.chat.get_configured_provider") as provider:
            response = self.post_chat("Đàn vật nuôi nào đang được ghi nhận?")
        self.assertIn(response.status_code, (401, 403))
        provider.assert_not_called()

    def test_invalid_or_oversized_question_is_rejected_before_provider(self):
        for payload in ({"question": ""}, {"question": "x" * 501},
                        {"question": "đàn vật nuôi", "context": {"secret": "private"}}):
            with self.subTest(payload=payload), patch("apps.ai.chat.get_configured_provider") as provider:
                response = self.client.post("/api/ai/chat", payload, content_type="application/json")
            self.assertEqual(response.status_code, 400)
            provider.assert_not_called()

    def test_chat_api_is_csrf_protected_for_session_clients(self):
        from django.test import Client

        client = Client(enforce_csrf_checks=True)
        client.force_login(self.users[ROLE_MANAGEMENT])
        self.assertEqual(client.post(
            "/api/ai/chat", {"question": "Đàn vật nuôi nào?"}, content_type="application/json",
        ).status_code, 403)

