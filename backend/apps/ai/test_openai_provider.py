"""Provider foundation tests: fake clients and SDK MockTransport only."""

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

from config.environment import get_ai_configuration, get_openai_configuration
from apps.herds.models import Herd
from apps.users.roles import ROLE_MANAGEMENT

from .openai_provider import OpenAIProvider, normalize_request
from .orchestrator import AIInvocationError, AIOrchestrator
from .providers import AIConfigurationError, AIErrorCategory, AIProviderError, AIRequest, AIResponse, get_configured_provider
from .safety import validate_and_normalize_output


FAKE_KEY = "fake-openai-key-for-tests-only"
PRIVATE_BODY = "fake-private-provider-payload"


def configuration(**overrides):
    return get_openai_configuration({"OPENAI_API_KEY": FAKE_KEY, **overrides})


def fake_client(text="  factual report  "):
    client = Mock()
    client.responses.create.return_value = SimpleNamespace(output_text=text)
    return client


class NoNetworkMixin:
    def setUp(self):
        super().setUp()
        guard = patch("socket.socket.connect", side_effect=AssertionError("Network forbidden in tests"))
        self.network_guard = guard.start()
        self.addCleanup(guard.stop)


class OpenAIConfigurationTests(NoNetworkMixin, SimpleTestCase):
    def test_approved_defaults(self):
        config = configuration()
        self.assertEqual(config.model, "gpt-5.6-terra")
        self.assertEqual(config.timeout_seconds, 30)
        self.assertEqual(config.max_retries, 0)
        self.assertEqual(config.max_input_bytes, 65536)

    def test_environment_overrides_and_provider_normalization(self):
        env = {"AI_PROVIDER": " OpenAI ", "OPENAI_API_KEY": FAKE_KEY,
               "OPENAI_MODEL": " configured-test-model ", "AI_TIMEOUT_SECONDS": "2.5",
               "OPENAI_MAX_RETRIES": "1", "AI_MAX_INPUT_BYTES": "128"}
        with patch.dict(os.environ, env, clear=True):
            config = get_openai_configuration()
            self.assertEqual(get_ai_configuration().provider, "openai")
        self.assertEqual((config.model, config.timeout_seconds, config.max_retries, config.max_input_bytes),
                         ("configured-test-model", 2.5, 1, 128))

    def test_production_factory_selects_openai_with_defaults(self):
        client = fake_client()
        with patch("apps.ai.openai_provider.OpenAI", return_value=client) as factory:
            provider = get_configured_provider({"AI_PROVIDER": "openai", "OPENAI_API_KEY": FAKE_KEY})
        self.assertIsInstance(provider, OpenAIProvider)
        self.assertIs(provider.client, client)
        factory.assert_called_once_with(api_key=FAKE_KEY, timeout=30, max_retries=0)

    def test_production_factory_reads_process_environment(self):
        with patch.dict(os.environ, {"AI_PROVIDER": "openai", "OPENAI_API_KEY": FAKE_KEY}, clear=True):
            with patch("apps.ai.openai_provider.OpenAI", return_value=fake_client()):
                self.assertIsInstance(get_configured_provider(), OpenAIProvider)

    def test_missing_key_never_falls_back_to_generic_key(self):
        with patch("apps.ai.openai_provider.OpenAI") as factory:
            for key in (None, "", "   "):
                env = {"AI_PROVIDER": "openai", "AI_API_KEY": FAKE_KEY}
                if key is not None:
                    env["OPENAI_API_KEY"] = key
                with self.subTest(key=key), self.assertRaises(AIConfigurationError) as raised:
                    get_configured_provider(env)
                self.assertEqual(raised.exception.category, AIErrorCategory.CONFIGURATION)
                self.assertNotIn(FAKE_KEY, str(raised.exception))
        factory.assert_not_called()

    def test_blank_model_rejected_safely(self):
        for value in ("", "  "):
            with self.subTest(value=value), self.assertRaises(AIConfigurationError):
                get_configured_provider({"AI_PROVIDER": "openai", "OPENAI_API_KEY": FAKE_KEY, "OPENAI_MODEL": value})

    def test_invalid_numeric_configuration_uses_safe_boundary(self):
        cases = {
            "AI_TIMEOUT_SECONDS": ("", "invalid", "0", "-1", "nan", "inf", "-inf"),
            "OPENAI_MAX_RETRIES": ("", "invalid", "-1", "1.5", "nan"),
            "AI_MAX_INPUT_BYTES": ("", "invalid", "0", "-1", "1.5"),
        }
        with patch("apps.ai.openai_provider.OpenAI") as factory:
            for name, values in cases.items():
                for value in values:
                    with self.subTest(name=name, value=value), self.assertRaises(AIConfigurationError) as raised:
                        get_configured_provider({"AI_PROVIDER": "openai", "OPENAI_API_KEY": FAKE_KEY, name: value})
                    self.assertNotIn(FAKE_KEY, str(raised.exception))
            with self.assertRaises(AIConfigurationError) as raised:
                get_configured_provider({"AI_PROVIDER": "openai", "OPENAI_API_KEY": FAKE_KEY, "AI_TIMEOUT_SECONDS": PRIVATE_BODY})
            self.assertNotIn(PRIVATE_BODY, ''.join(traceback.format_exception(raised.exception)))
        factory.assert_not_called()

    def test_legacy_injected_factory_contract_is_preserved(self):
        provider = Mock()
        factory = Mock(return_value=provider)
        actual = get_configured_provider({"AI_PROVIDER": "fake", "AI_API_KEY": "fake-generic-key"}, {"fake": factory})
        self.assertIs(actual, provider)
        factory.assert_called_once_with("fake-generic-key")

    def test_explicit_registry_is_authoritative(self):
        with self.assertRaisesRegex(AIConfigurationError, "not supported"):
            get_configured_provider({"AI_PROVIDER": "openai", "OPENAI_API_KEY": FAKE_KEY}, {})

    def test_missing_and_unknown_providers_are_safe(self):
        for env in ({}, {"AI_PROVIDER": "not-supported"}):
            with self.subTest(env=env), self.assertRaises(AIConfigurationError):
                get_configured_provider(env)

    def test_client_factory_failure_has_no_sensitive_exception_chain(self):
        with patch("apps.ai.openai_provider.OpenAI", side_effect=RuntimeError(FAKE_KEY + PRIVATE_BODY)):
            with self.assertRaises(AIConfigurationError) as raised:
                get_configured_provider({"AI_PROVIDER": "openai", "OPENAI_API_KEY": FAKE_KEY})
        rendered = ''.join(traceback.format_exception(raised.exception))
        self.assertNotIn(FAKE_KEY, rendered)
        self.assertNotIn(PRIVATE_BODY, rendered)

    def test_configuration_repr_does_not_expose_credentials(self):
        self.assertNotIn(FAKE_KEY, repr(configuration()))
        self.assertNotIn(FAKE_KEY, repr(get_ai_configuration({"AI_API_KEY": FAKE_KEY})))


class OpenAIProviderTests(NoNetworkMixin, SimpleTestCase):
    def setUp(self):
        super().setUp()
        self.client_mock = fake_client()
        self.provider = OpenAIProvider(configuration(), client=self.client_mock)
        self.request = AIRequest("Preserve supplied facts and metrics.", {"herd": {"id": 1, "name": "Đàn bò"}, "metrics": {"average_weight": Decimal("12.50")}})

    def test_injected_client_factory_receives_configuration(self):
        factory = Mock(return_value=self.client_mock)
        OpenAIProvider(configuration(AI_TIMEOUT_SECONDS="4", OPENAI_MAX_RETRIES="2"), client_factory=factory)
        factory.assert_called_once_with(api_key=FAKE_KEY, timeout=4, max_retries=2)

    def test_mapping_preserves_prompt_context_and_configured_model(self):
        provider = OpenAIProvider(configuration(OPENAI_MODEL="configured-test-model"), client=self.client_mock)
        response = provider.generate(self.request)
        sent = self.client_mock.responses.create.call_args.kwargs
        self.assertEqual(set(sent), {"model", "store", "truncation", "instructions", "input"})
        self.assertEqual(sent["model"], "configured-test-model")
        self.assertIs(sent["store"], False)
        self.assertEqual(sent["truncation"], "disabled")
        self.assertEqual(sent["instructions"], self.request.prompt)
        self.assertEqual(json.loads(sent["input"]), {"herd": {"id": 1, "name": "Đàn bò"}, "metrics": {"average_weight": "12.50"}})
        self.assertEqual(response, AIResponse("  factual report  ", "openai"))
        self.assertNotIn(FAKE_KEY, str(sent))

    def test_normalization_is_stable_utf8_and_only_sent_content(self):
        first = AIRequest("facts", {"z": "Đàn", "a": Decimal("1.20")})
        second = AIRequest("facts", {"a": Decimal("1.20"), "z": "Đàn"})
        content, encoded = normalize_request(first)
        self.assertEqual(encoded, normalize_request(second)[1])
        self.assertEqual(encoded, json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        self.assertGreater(len(encoded), len(encoded.decode("utf-8")))
        self.provider.generate(first)
        sent = self.client_mock.responses.create.call_args.kwargs
        self.assertEqual(content, {key: sent[key] for key in ("instructions", "input")})

    def test_exact_65536_byte_payload_is_allowed_without_truncation(self):
        base = AIRequest("", {"notes": "Đàn bò"})
        padding = 65536 - len(normalize_request(base)[1])
        request = AIRequest("x" * padding, base.context)
        self.assertEqual(len(normalize_request(request)[1]), 65536)
        self.provider.generate(request)
        self.assertEqual(self.client_mock.responses.create.call_args.kwargs["instructions"], request.prompt)

    def test_payload_one_byte_over_limit_never_calls_provider(self):
        base = AIRequest("", {})
        request = AIRequest("x" * (65537 - len(normalize_request(base)[1])), {})
        self.assertEqual(len(normalize_request(request)[1]), 65537)
        with self.assertRaises(AIProviderError) as raised:
            self.provider.generate(request)
        self.assertEqual(raised.exception.category, AIErrorCategory.INPUT_TOO_LARGE)
        self.client_mock.responses.create.assert_not_called()

    def test_custom_limit_applies_to_multibyte_context_as_well_as_prompt(self):
        size = len(normalize_request(self.request)[1])
        provider = OpenAIProvider(replace(configuration(), max_input_bytes=size - 1), client=self.client_mock)
        with self.assertRaises(AIProviderError):
            provider.generate(self.request)
        self.client_mock.responses.create.assert_not_called()

    def test_all_records_reach_provider_and_input_is_not_mutated(self):
        records = [{"measurement_date": "2026-01-01", "weight": Decimal("1.25"), "notes": str(i)} for i in range(40)]
        request = AIRequest("Preserve all metrics", {"growth_records": records})
        self.provider.generate(request)
        sent = json.loads(self.client_mock.responses.create.call_args.kwargs["input"])
        self.assertEqual(len(sent["growth_records"]), 40)
        self.assertEqual([row["notes"] for row in sent["growth_records"]], [str(i) for i in range(40)])
        self.assertIsInstance(records[0]["weight"], Decimal)

    def test_unserializable_or_nonfinite_data_fails_without_provider_call(self):
        for context in ({"v": object()}, {"v": float("nan")}, {"v": Decimal("Infinity")}):
            with self.subTest(context_type=type(context["v"])), self.assertRaises(AIProviderError) as raised:
                self.provider.generate(AIRequest("facts", context))
            self.assertEqual(raised.exception.category, AIErrorCategory.INVALID_REQUEST)
        self.client_mock.responses.create.assert_not_called()

    def test_empty_and_invalid_response_text_rejected_safely(self):
        for value in (None, "", " \n ", 12):
            self.client_mock.responses.create.return_value = SimpleNamespace(output_text=value)
            with self.subTest(value=value), self.assertRaises(AIProviderError) as raised:
                self.provider.generate(self.request)
            self.assertEqual(raised.exception.category, AIErrorCategory.INVALID_RESPONSE)

    def test_missing_output_accessor_is_safe(self):
        self.client_mock.responses.create.return_value = {"text": PRIVATE_BODY}
        with self.assertRaises(AIProviderError) as raised:
            self.provider.generate(self.request)
        self.assertEqual(raised.exception.category, AIErrorCategory.INVALID_RESPONSE)
        self.assertNotIn(PRIVATE_BODY, str(raised.exception))

    def test_sdk_exception_categories_and_exception_text_are_safe(self):
        request = httpx2.Request("POST", "https://provider.invalid/v1/responses")
        response = lambda status: httpx2.Response(status, request=request)
        cases = [
            (openai.APITimeoutError(request=request), AIErrorCategory.TIMEOUT),
            (openai.RateLimitError(PRIVATE_BODY, response=response(429), body={"key": FAKE_KEY}), AIErrorCategory.RATE_LIMIT),
            (openai.AuthenticationError(PRIVATE_BODY, response=response(401), body={"key": FAKE_KEY}), AIErrorCategory.AUTHENTICATION),
            (openai.PermissionDeniedError(PRIVATE_BODY, response=response(403), body=None), AIErrorCategory.AUTHENTICATION),
            (openai.APIConnectionError(message=PRIVATE_BODY, request=request), AIErrorCategory.CONNECTION),
            (openai.BadRequestError(PRIVATE_BODY, response=response(400), body=None), AIErrorCategory.INVALID_REQUEST),
            (openai.NotFoundError(PRIVATE_BODY, response=response(404), body=None), AIErrorCategory.INVALID_REQUEST),
            (openai.InternalServerError(PRIVATE_BODY, response=response(500), body=None), AIErrorCategory.PROVIDER_FAILURE),
            (RuntimeError(FAKE_KEY + PRIVATE_BODY), AIErrorCategory.PROVIDER_FAILURE),
        ]
        for error, expected in cases:
            self.client_mock.responses.create.side_effect = error
            with self.subTest(error=type(error).__name__), self.assertRaises(AIProviderError) as raised:
                self.provider.generate(self.request)
            self.assertEqual(raised.exception.category, expected)
            rendered = ''.join(traceback.format_exception(raised.exception))
            self.assertNotIn(FAKE_KEY, rendered)
            self.assertNotIn(PRIVATE_BODY, rendered)

    def test_orchestrator_preserves_category_and_safe_logs(self):
        self.client_mock.responses.create.side_effect = openai.APITimeoutError(request=httpx2.Request("POST", "https://provider.invalid"))
        with patch("apps.ai.orchestrator.get_user_role", return_value=ROLE_MANAGEMENT):
            with self.assertLogs("apps.ai.orchestrator", level="WARNING") as logs:
                with self.assertRaises(AIInvocationError) as raised:
                    AIOrchestrator(self.provider).run(object(), PRIVATE_BODY, {"notes": FAKE_KEY})
        self.assertEqual(raised.exception.category, AIErrorCategory.TIMEOUT)
        for private in (FAKE_KEY, PRIVATE_BODY):
            self.assertNotIn(private, str(raised.exception))
            self.assertNotIn(private, '\n'.join(logs.output))

    def test_shared_output_validator_still_runs(self):
        with patch("apps.ai.orchestrator.get_user_role", return_value=ROLE_MANAGEMENT):
            with patch("apps.ai.orchestrator.validate_and_normalize_output", wraps=validate_and_normalize_output) as validator:
                result = AIOrchestrator(self.provider).run(object(), self.request.prompt, self.request.context)
        validator.assert_called_once()
        self.assertEqual(result, AIResponse("factual report", "openai"))

    def test_official_sdk_round_trip_uses_mock_transport_only(self):
        captured = []
        def respond(request):
            captured.append(json.loads(request.content))
            return httpx2.Response(200, json={
                "id": "resp_fake", "object": "response", "created_at": 0,
                "model": "gpt-5.6-terra", "status": "completed",
                "output": [{"id": "msg_fake", "type": "message", "role": "assistant", "status": "completed",
                            "content": [{"type": "output_text", "text": "mock SDK output", "annotations": []}]}],
            })
        with httpx2.Client(transport=httpx2.MockTransport(respond)) as http_client:
            with openai.OpenAI(api_key=FAKE_KEY, http_client=http_client, timeout=30, max_retries=0) as sdk_client:
                result = OpenAIProvider(configuration(), client=sdk_client).generate(self.request)
        self.assertEqual(result, AIResponse("mock SDK output", "openai"))
        self.assertEqual(len(captured), 1)
        self.assertIs(captured[0]["store"], False)
        self.assertEqual(captured[0]["instructions"], self.request.prompt)
        self.assertEqual(json.loads(captured[0]["input"])["metrics"]["average_weight"], "12.50")
        self.network_guard.assert_not_called()

    def test_official_sdk_does_not_retry_with_approved_policy(self):
        calls = []
        def respond(request):
            calls.append(request)
            return httpx2.Response(429, json={"error": {"message": PRIVATE_BODY}})
        with httpx2.Client(transport=httpx2.MockTransport(respond)) as http_client:
            factory = lambda **kwargs: openai.OpenAI(http_client=http_client, **kwargs)
            provider = OpenAIProvider(configuration(), client_factory=factory)
            try:
                with self.assertRaises(AIProviderError) as raised:
                    provider.generate(self.request)
            finally:
                provider.client.close()
        self.assertEqual(raised.exception.category, AIErrorCategory.RATE_LIMIT)
        self.assertEqual(len(calls), 1)
        self.network_guard.assert_not_called()


class MissingOpenAIConfigurationManagementTests(NoNetworkMixin, TestCase):
    def test_non_ai_management_remains_available_with_invalid_ai_config(self):
        user = get_user_model().objects.create_user(username="foundation-manager")
        user.groups.add(Group.objects.get(name=ROLE_MANAGEMENT))
        herd = Herd.objects.create(code="FOUNDATION", name="Herd", animal_type="cattle", management_mode="group", quantity=1, status="active")
        self.client.force_login(user)
        with patch.dict(os.environ, {"AI_PROVIDER": "openai", "OPENAI_API_KEY": "", "AI_TIMEOUT_SECONDS": "invalid"}):
            response = self.client.get(f"/api/herds/{herd.pk}/")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["code"], herd.code)
            response = self.client.get("/ai/")
            self.assertContains(response, "AI hiện chưa được cấu hình")
        self.assertEqual(Herd.objects.count(), 1)
