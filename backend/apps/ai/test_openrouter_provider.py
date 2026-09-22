"""Offline foundation evidence, not proof of live OpenRouter/model compatibility."""

import json
import os
import traceback
from dataclasses import replace
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

import httpx2
import openai
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import SimpleTestCase, TestCase

from apps.herds.models import Herd
from apps.users.roles import ROLE_MANAGEMENT
from config.environment import get_openrouter_configuration

from .errors import public_ai_error
from .openai_provider import OpenAIProvider, normalize_request
from .openrouter_provider import OpenRouterProvider
from .orchestrator import AIInvocationError, AIOrchestrator
from .prompts.growth_report import build_growth_report_prompt
from .providers import AIConfigurationError, AIErrorCategory, AIProviderError, AIRequest, AIResponse, get_configured_provider


MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
BASE_URL = "https://openrouter.ai/api/v1"
FAKE_KEY = "fake-openrouter-test-key-only"
PRIVATE = "private-provider-response-body"


def configuration(**overrides):
    return get_openrouter_configuration({"OPENROUTER_API_KEY": FAKE_KEY, **overrides})


def fake_client(text="  report  "):
    client = Mock()
    client.responses.create.return_value = SimpleNamespace(output_text=text)
    return client


def request_for_test(context=None):
    spec = build_growth_report_prompt()
    return AIRequest(spec.system_prompt, spec.user_prompt,
                     context if context is not None else {"herd": {"id": 1, "name": "Đàn bò"}, "metrics": {"average_weight": Decimal("12.50")}},
                     spec.version, spec.output_constraints)


class NoNetwork:
    def setUp(self):
        super().setUp()
        guard = patch("socket.socket.connect", side_effect=AssertionError("Network forbidden"))
        self.network_guard = guard.start()
        self.addCleanup(guard.stop)
        self.addCleanup(self.network_guard.assert_not_called)


class OpenRouterConfigurationTests(NoNetwork, SimpleTestCase):
    def test_approved_defaults(self):
        config = configuration()
        self.assertEqual((config.model, config.base_url, config.timeout_seconds, config.max_retries, config.max_input_bytes),
                         (MODEL, BASE_URL, 30, 0, 65536))
        self.assertEqual(openai.__version__, "3.16.2")

    def test_factory_selects_openrouter_and_passes_exact_client_configuration(self):
        client = fake_client()
        with patch("apps.ai.openrouter_provider.OpenAI", return_value=client) as factory:
            provider = get_configured_provider({"AI_PROVIDER": " OpenRouter ", "OPENROUTER_API_KEY": FAKE_KEY})
        self.assertIsInstance(provider, OpenRouterProvider)
        self.assertEqual(provider.name, "openrouter")
        self.assertIs(provider.client, client)
        factory.assert_called_once_with(api_key=FAKE_KEY, base_url=BASE_URL, timeout=30, max_retries=0)

    def test_openai_selection_and_credentials_are_unchanged(self):
        with patch("apps.ai.openai_provider.OpenAI", return_value=fake_client()) as factory:
            provider = get_configured_provider({"AI_PROVIDER": "openai", "OPENAI_API_KEY": "fake-openai-key", "OPENROUTER_API_KEY": FAKE_KEY})
        self.assertIs(type(provider), OpenAIProvider)
        factory.assert_called_once_with(api_key="fake-openai-key", timeout=30, max_retries=0)

    def test_missing_openrouter_key_never_falls_back_to_openai_or_generic(self):
        for key in (None, "", "   "):
            env = {"AI_PROVIDER": "openrouter", "OPENAI_API_KEY": "fake-other-key", "AI_API_KEY": "fake-generic-key"}
            if key is not None:
                env["OPENROUTER_API_KEY"] = key
            with patch("apps.ai.openrouter_provider.OpenAI") as factory:
                with self.assertRaises(AIConfigurationError) as raised:
                    get_configured_provider(env)
            self.assertEqual(raised.exception.category, AIErrorCategory.CONFIGURATION)
            factory.assert_not_called()

    def test_openrouter_key_never_satisfies_openai(self):
        with patch("apps.ai.openai_provider.OpenAI") as factory:
            with self.assertRaises(AIConfigurationError):
                get_configured_provider({"AI_PROVIDER": "openai", "OPENROUTER_API_KEY": FAKE_KEY})
        factory.assert_not_called()

    def test_blank_model_or_base_url_is_safe_configuration_failure(self):
        for field in ("OPENROUTER_MODEL", "OPENROUTER_BASE_URL"):
            for value in ("", "  "):
                with self.subTest(field=field, value=value), self.assertRaises(AIConfigurationError):
                    get_configured_provider({"AI_PROVIDER": "openrouter", "OPENROUTER_API_KEY": FAKE_KEY, field: value})

    def test_malformed_numeric_configuration_never_constructs_client(self):
        cases = {
            "AI_TIMEOUT_SECONDS": ("", "bad", "0", "-1", "nan", "inf"),
            "OPENROUTER_MAX_RETRIES": ("", "bad", "-1", "1.5"),
            "AI_MAX_INPUT_BYTES": ("", "bad", "0", "-1", "1.5"),
        }
        with patch("apps.ai.openrouter_provider.OpenAI") as factory:
            for field, values in cases.items():
                for value in values:
                    with self.subTest(field=field, value=value), self.assertRaises(AIConfigurationError):
                        get_configured_provider({"AI_PROVIDER": "openrouter", "OPENROUTER_API_KEY": FAKE_KEY, field: value})
        factory.assert_not_called()

    def test_environment_values_and_explicit_retry_override_reach_client(self):
        env = {"AI_PROVIDER": "openrouter", "OPENROUTER_API_KEY": FAKE_KEY,
               "OPENROUTER_MODEL": " " + MODEL + " ", "OPENROUTER_BASE_URL": " " + BASE_URL + " ",
               "AI_TIMEOUT_SECONDS": "2.5", "OPENROUTER_MAX_RETRIES": "1", "AI_MAX_INPUT_BYTES": "128"}
        with patch.dict(os.environ, env, clear=True), patch("apps.ai.openrouter_provider.OpenAI", return_value=fake_client()) as factory:
            provider = get_configured_provider()
        self.assertEqual(provider.configuration.model, MODEL)
        self.assertEqual(provider.configuration.max_input_bytes, 128)
        factory.assert_called_once_with(api_key=FAKE_KEY, base_url=BASE_URL, timeout=2.5, max_retries=1)

    def test_injected_registry_remains_authoritative(self):
        provider = Mock()
        factory = Mock(return_value=provider)
        self.assertIs(get_configured_provider({"AI_PROVIDER": "fake", "AI_API_KEY": "fake-registry-key"}, {"fake": factory}), provider)
        factory.assert_called_once_with("fake-registry-key")
        with self.assertRaises(AIConfigurationError):
            get_configured_provider({"AI_PROVIDER": "openrouter", "OPENROUTER_API_KEY": FAKE_KEY}, {})
        with self.assertRaises(AIConfigurationError):
            get_configured_provider({"AI_PROVIDER": "unsupported"})

    def test_client_constructor_failure_hides_secrets_and_configuration_repr(self):
        with patch("apps.ai.openrouter_provider.OpenAI", side_effect=RuntimeError(FAKE_KEY + PRIVATE)):
            with self.assertRaises(AIConfigurationError) as raised:
                get_configured_provider({"AI_PROVIDER": "openrouter", "OPENROUTER_API_KEY": FAKE_KEY})
        rendered = "".join(traceback.format_exception(raised.exception)) + repr(configuration())
        self.assertNotIn(FAKE_KEY, rendered)
        self.assertNotIn(PRIVATE, rendered)


class OpenRouterProviderTests(NoNetwork, SimpleTestCase):
    def setUp(self):
        super().setUp()
        self.client = fake_client()
        self.provider = OpenRouterProvider(configuration(), client=self.client)
        self.request = request_for_test()

    def test_reuses_identical_transport_and_size_guard(self):
        self.assertIs(OpenRouterProvider.generate, OpenAIProvider.generate)

    def test_explicit_prompt_fields_and_transient_request_map_without_tools_or_fallbacks(self):
        result = self.provider.generate(self.request)
        sent = self.client.responses.create.call_args.kwargs
        self.assertEqual(set(sent), {"model", "instructions", "input", "store", "truncation"})
        self.assertEqual(sent["model"], MODEL)
        self.assertIs(sent["store"], False)
        self.assertEqual(sent["truncation"], "disabled")
        self.assertEqual(sent["instructions"], self.request.system_prompt + "\n\nOutput constraints:\n" + "\n".join(self.request.output_constraints))
        self.assertEqual(json.loads(sent["input"]), {
            "user_prompt": self.request.user_prompt, "prompt_version": "growth-report-v1",
            "context": {"herd": {"id": 1, "name": "Đàn bò"}, "metrics": {"average_weight": "12.50"}},
        })
        self.assertEqual(result, AIResponse("  report  ", "openrouter"))
        self.assertNotIn(FAKE_KEY, str(sent))

    def test_deterministic_multibyte_serialization(self):
        a = request_for_test({"z": "Đàn bò", "a": Decimal("12.50")})
        b = request_for_test({"a": Decimal("12.50"), "z": "Đàn bò"})
        content, encoded = normalize_request(a)
        self.assertEqual(encoded, normalize_request(b)[1])
        self.assertEqual(encoded, json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        self.assertGreater(len(encoded), len(encoded.decode("utf-8")))

    def test_explicit_model_configuration_propagates_to_fake_client_only(self):
        # Configuration remains environment-driven like the existing provider.
        # This is a fake-only sentinel, never a KT3 evaluation model selection.
        provider = OpenRouterProvider(configuration(OPENROUTER_MODEL="offline-test-model"), client=self.client)
        provider.generate(self.request)
        sent = self.client.responses.create.call_args.kwargs
        self.assertEqual(sent["model"], "offline-test-model")
        self.assertNotIn("models", sent)

    def test_exact_65536_bytes_allowed(self):
        base = request_for_test({"notes": "Đàn bò"})
        exact = replace(base, user_prompt=base.user_prompt + "x" * (65536 - len(normalize_request(base)[1])))
        self.assertEqual(len(normalize_request(exact)[1]), 65536)
        self.provider.generate(exact)
        self.client.responses.create.assert_called_once()

    def test_65537_bytes_blocked_before_sdk(self):
        base = request_for_test({})
        over = replace(base, user_prompt=base.user_prompt + "x" * (65537 - len(normalize_request(base)[1])))
        self.assertEqual(len(normalize_request(over)[1]), 65537)
        with self.assertRaises(AIProviderError) as raised:
            self.provider.generate(over)
        self.assertEqual(raised.exception.category, AIErrorCategory.INPUT_TOO_LARGE)
        self.assertEqual(public_ai_error(raised.exception).status_code, 413)
        self.client.responses.create.assert_not_called()

    def test_all_records_sent_without_mutating_or_truncating_context(self):
        records = [{"notes": str(i), "weight": Decimal("1.25")} for i in range(50)]
        self.provider.generate(request_for_test({"growth_records": records}))
        data = json.loads(self.client.responses.create.call_args.kwargs["input"])["context"]
        self.assertEqual([row["notes"] for row in data["growth_records"]], [str(i) for i in range(50)])
        self.assertIsInstance(records[0]["weight"], Decimal)

    def test_empty_invalid_and_missing_output_accessor_fail_safely(self):
        for response in (SimpleNamespace(output_text=""), SimpleNamespace(output_text="  "),
                         SimpleNamespace(output_text=None), SimpleNamespace(output_text=1), {"text": PRIVATE}):
            self.client.responses.create.return_value = response
            with self.assertRaises(AIProviderError) as raised:
                self.provider.generate(self.request)
            self.assertEqual(raised.exception.category, AIErrorCategory.INVALID_RESPONSE)
            self.assertNotIn(PRIVATE, str(raised.exception))

    def test_invalid_context_is_rejected_locally(self):
        for value in (object(), Decimal("Infinity"), float("nan")):
            with self.assertRaises(AIProviderError):
                self.provider.generate(request_for_test({"invalid": value}))
        self.client.responses.create.assert_not_called()

    def test_sdk_exception_categories_and_public_statuses_are_preserved(self):
        req = httpx2.Request("POST", BASE_URL + "/responses")
        response = lambda code: httpx2.Response(code, request=req)
        cases = (
            (openai.APITimeoutError(request=req), AIErrorCategory.TIMEOUT, 504),
            (openai.RateLimitError(PRIVATE, response=response(429), body={"key": FAKE_KEY}), AIErrorCategory.RATE_LIMIT, 429),
            (openai.APIConnectionError(message=PRIVATE, request=req), AIErrorCategory.CONNECTION, 502),
            (openai.AuthenticationError(PRIVATE, response=response(401), body=None), AIErrorCategory.AUTHENTICATION, 503),
            (openai.PermissionDeniedError(PRIVATE, response=response(403), body=None), AIErrorCategory.AUTHENTICATION, 503),
            (openai.BadRequestError(PRIVATE, response=response(400), body=None), AIErrorCategory.INVALID_REQUEST, 503),
            (openai.NotFoundError(PRIVATE, response=response(404), body=None), AIErrorCategory.INVALID_REQUEST, 503),
            (openai.APIResponseValidationError(response(200), {"key": FAKE_KEY}, message=PRIVATE), AIErrorCategory.INVALID_RESPONSE, 502),
            (RuntimeError(FAKE_KEY + PRIVATE), AIErrorCategory.PROVIDER_FAILURE, 502),
        )
        for error, category, status in cases:
            self.client.responses.create.side_effect = error
            with self.subTest(category=category), self.assertRaises(AIProviderError) as raised:
                self.provider.generate(self.request)
            self.assertEqual(raised.exception.category, category)
            self.assertEqual(public_ai_error(raised.exception).status_code, status)
            rendered = "".join(traceback.format_exception(raised.exception))
            self.assertNotIn(PRIVATE, rendered)
            self.assertNotIn(FAKE_KEY, rendered)

    def test_orchestrator_normalizes_output_and_logs_only_safe_failure(self):
        with patch("apps.ai.orchestrator.get_user_role", return_value=ROLE_MANAGEMENT):
            result = AIOrchestrator(self.provider).run(object(), build_growth_report_prompt(), self.request.context)
            self.assertEqual(result, AIResponse("report", "openrouter"))
            self.client.responses.create.side_effect = RuntimeError(FAKE_KEY + PRIVATE)
            with self.assertLogs("apps.ai.orchestrator", level="WARNING") as logs:
                with self.assertRaises(AIInvocationError):
                    AIOrchestrator(self.provider).run(object(), build_growth_report_prompt(), {"notes": PRIVATE})
        for value in (FAKE_KEY, PRIVATE, self.request.system_prompt, self.request.user_prompt):
            self.assertNotIn(value, "\n".join(logs.output))

    def test_sdk_mock_transport_proves_custom_base_url_path_headers_and_shape(self):
        captured = []
        def respond(request):
            captured.append(request)
            return httpx2.Response(200, json={
                "id": "resp_fake", "object": "response", "created_at": 0, "model": MODEL, "status": "completed",
                "output": [{"id": "msg_fake", "type": "message", "role": "assistant", "status": "completed",
                            "content": [{"type": "output_text", "text": "mock response", "annotations": []}]}],
            })
        with httpx2.Client(transport=httpx2.MockTransport(respond)) as http_client:
            provider = OpenRouterProvider(configuration(), client_factory=lambda **kwargs: openai.OpenAI(http_client=http_client, **kwargs))
            try:
                result = provider.generate(self.request)
            finally:
                provider.client.close()
        self.assertEqual(result, AIResponse("mock response", "openrouter"))
        self.assertEqual(len(captured), 1)
        self.assertEqual(str(captured[0].url), BASE_URL + "/responses")
        self.assertEqual(captured[0].method, "POST")
        self.assertEqual(captured[0].headers["authorization"], "Bearer " + FAKE_KEY)
        body = json.loads(captured[0].content)
        self.assertEqual(body, {"model": MODEL, "store": False, "truncation": "disabled", **normalize_request(self.request)[0]})
        self.assertNotIn(FAKE_KEY, captured[0].content.decode())

    def test_real_sdk_transport_rate_limit_has_no_retry(self):
        calls = []
        def respond(request):
            calls.append(request)
            return httpx2.Response(429, json={"error": {"message": PRIVATE}})
        with httpx2.Client(transport=httpx2.MockTransport(respond)) as http_client:
            provider = OpenRouterProvider(configuration(), client_factory=lambda **kwargs: openai.OpenAI(http_client=http_client, **kwargs))
            try:
                with self.assertRaises(AIProviderError) as raised:
                    provider.generate(self.request)
            finally:
                provider.client.close()
        self.assertEqual(raised.exception.category, AIErrorCategory.RATE_LIMIT)
        self.assertEqual(len(calls), 1)


class OpenRouterManagementTests(NoNetwork, TestCase):
    def test_missing_configuration_does_not_block_management_or_safe_ai_page(self):
        user = get_user_model().objects.create_user(username="router-manager")
        user.groups.add(Group.objects.get(name=ROLE_MANAGEMENT))
        herd = Herd.objects.create(code="ROUTER", name="Herd", animal_type="cattle", management_mode="group", quantity=1, status="active")
        self.client.force_login(user)
        with patch.dict(os.environ, {"AI_PROVIDER": "openrouter", "OPENROUTER_API_KEY": "", "OPENAI_API_KEY": FAKE_KEY}), patch("apps.ai.openrouter_provider.OpenAI") as factory:
            self.assertEqual(self.client.get(f"/api/herds/{herd.pk}/").status_code, 200)
            self.assertContains(self.client.get("/ai/"), "AI hiện chưa được cấu hình")
            response = self.client.post("/api/ai/herd-summary", {"herd_id": herd.pk}, content_type="application/json")
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response.json()["error_code"], "ai_configuration_unavailable")
            self.assertNotIn(FAKE_KEY, response.content.decode())
        factory.assert_not_called()
        self.assertEqual(Herd.objects.count(), 1)
