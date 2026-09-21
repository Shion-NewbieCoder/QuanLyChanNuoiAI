"""OpenAI Responses adapter. No domain queries, persistence or feature prompts."""

import json
from decimal import Decimal

from openai import (
    APIConnectionError,
    APIResponseValidationError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    OpenAI,
    PermissionDeniedError,
    RateLimitError,
)

from config.environment import OpenAIConfiguration

from .providers import AIConfigurationError, AIErrorCategory, AIProviderError, AIRequest, AIResponse


def _json_value(value):
    # Existing Growth Report context uses Decimal; preserve its exact value.
    if isinstance(value, Decimal) and value.is_finite():
        return str(value)
    raise TypeError("Unsupported AI context value.")


def _serialize(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False, default=_json_value,
    )


def normalize_request(request: AIRequest):
    """Serialize exactly the provider-bound content measured by the UTF-8 guard."""
    try:
        if (
            not all(isinstance(value, str) for value in (
                request.system_prompt, request.user_prompt, request.prompt_version
            ))
            or not isinstance(request.context, dict)
            or not isinstance(request.output_constraints, tuple)
            or not all(isinstance(value, str) for value in request.output_constraints)
        ):
            raise TypeError
        content = {
            "instructions": request.system_prompt + "\n\nOutput constraints:\n"
            + "\n".join(request.output_constraints),
            "input": _serialize({
                "user_prompt": request.user_prompt,
                "context": request.context,
                "prompt_version": request.prompt_version,
            }),
        }
        encoded = _serialize(content).encode("utf-8")
    except (TypeError, ValueError, UnicodeError, OverflowError, RecursionError):
        raise AIProviderError(
            "AI request content is invalid.", category=AIErrorCategory.INVALID_REQUEST
        ) from None
    return content, encoded


class OpenAIProvider:
    name = "openai"

    def __init__(self, configuration: OpenAIConfiguration, *, client=None, client_factory=None):
        self.configuration = configuration
        if client is not None:
            self.client = client
            return
        factory = OpenAI if client_factory is None else client_factory
        try:
            self.client = factory(
                api_key=configuration.api_key,
                timeout=configuration.timeout_seconds,
                max_retries=configuration.max_retries,
            )
        except Exception:
            raise AIConfigurationError("AI provider configuration is invalid.") from None

    def generate(self, request: AIRequest) -> AIResponse:
        content, encoded = normalize_request(request)
        if len(encoded) > self.configuration.max_input_bytes:
            raise AIProviderError(
                "AI input is too large.", category=AIErrorCategory.INPUT_TOO_LARGE
            )
        try:
            response = self.client.responses.create(
                model=self.configuration.model, store=False, truncation="disabled", **content
            )
        except APITimeoutError:
            raise AIProviderError("AI provider timed out.", category=AIErrorCategory.TIMEOUT) from None
        except RateLimitError:
            raise AIProviderError("AI provider rate limit reached.", category=AIErrorCategory.RATE_LIMIT) from None
        except (AuthenticationError, PermissionDeniedError):
            raise AIProviderError("AI provider authentication failed.", category=AIErrorCategory.AUTHENTICATION) from None
        except APIConnectionError:
            raise AIProviderError("AI provider connection failed.", category=AIErrorCategory.CONNECTION) from None
        except (BadRequestError, NotFoundError):
            raise AIProviderError("AI provider model or request is invalid.", category=AIErrorCategory.INVALID_REQUEST) from None
        except APIResponseValidationError:
            raise AIProviderError("AI provider returned an invalid response.", category=AIErrorCategory.INVALID_RESPONSE) from None
        except Exception:
            raise AIProviderError("AI provider is unavailable.") from None

        try:
            text = response.output_text
        except Exception:
            raise AIProviderError("AI provider returned an invalid response.", category=AIErrorCategory.INVALID_RESPONSE) from None
        if not isinstance(text, str) or not text.strip():
            raise AIProviderError("AI provider returned an empty or invalid response.", category=AIErrorCategory.INVALID_RESPONSE)
        # AIOrchestrator still runs the shared authoritative output validator.
        return AIResponse(text=text, provider=self.name)
