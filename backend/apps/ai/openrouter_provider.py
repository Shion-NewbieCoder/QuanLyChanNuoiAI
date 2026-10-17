"""OpenRouter adapter using its documented Chat Completions endpoint."""

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

from config.environment import OpenRouterConfiguration

from .openai_provider import OpenAIProvider, normalize_request
from .providers import AIConfigurationError, AIErrorCategory, AIProviderError, AIResponse


class OpenRouterProvider(OpenAIProvider):
    """Keep the existing configuration and serializer, with OpenRouter's chat API."""

    name = "openrouter"

    def __init__(self, configuration: OpenRouterConfiguration, *, client=None, client_factory=None):
        self.configuration = configuration
        if client is not None:
            self.client = client
            return
        factory = OpenAI if client_factory is None else client_factory
        try:
            self.client = factory(
                api_key=configuration.api_key,
                base_url=configuration.base_url,
                timeout=configuration.timeout_seconds,
                max_retries=configuration.max_retries,
            )
        except Exception:
            raise AIConfigurationError("AI provider configuration is invalid.") from None

    def generate(self, request):
        if request.prompt_version != "livestock-chat-v1":
            return super().generate(request)

        content, encoded = normalize_request(request)
        if len(encoded) > self.configuration.max_input_bytes:
            raise AIProviderError(
                "AI input is too large.", category=AIErrorCategory.INPUT_TOO_LARGE
            )

        messages = [
            {"role": "system", "content": content["instructions"]},
            {"role": "user", "content": content["input"]},
        ]
        try:
            response = self.client.chat.completions.create(
                model=self.configuration.model,
                messages=messages,
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
            text = response.choices[0].message.content
        except Exception:
            raise AIProviderError("AI provider returned an invalid response.", category=AIErrorCategory.INVALID_RESPONSE) from None
        if not isinstance(text, str) or not text.strip():
            raise AIProviderError(
                "AI provider returned an empty or invalid response.",
                category=AIErrorCategory.INVALID_RESPONSE,
            )
        return AIResponse(text=text, provider=self.name)
