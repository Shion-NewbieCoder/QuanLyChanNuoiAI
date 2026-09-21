from dataclasses import dataclass
from enum import StrEnum
from typing import Callable, Mapping, Protocol

from config.environment import AIEnvironmentError, get_ai_configuration, get_openai_configuration


class AIErrorCategory(StrEnum):
    CONFIGURATION = "configuration_unavailable"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    CONNECTION = "connection"
    INVALID_REQUEST = "invalid_model_or_request"
    PROVIDER_FAILURE = "provider_failure"
    INPUT_TOO_LARGE = "input_too_large"
    INVALID_RESPONSE = "invalid_response"


class AIError(Exception):
    """Categorized application failure; presentation must never use its message."""

    category = AIErrorCategory.PROVIDER_FAILURE

    def __init__(self, message, *, category=None):
        super().__init__(message)
        self.category = AIErrorCategory(category if category is not None else self.category)


class AIConfigurationError(AIError):
    """Safe error raised when an AI provider cannot be configured."""

    category = AIErrorCategory.CONFIGURATION


class AIProviderError(AIError):
    """Safe provider-boundary error; provider details remain internal."""


@dataclass(frozen=True)
class AIRequest:
    system_prompt: str
    user_prompt: str
    context: dict[str, object]
    prompt_version: str
    output_constraints: tuple[str, ...]


@dataclass(frozen=True)
class AIResponse:
    text: str
    provider: str


class AIProviderInterface(Protocol):
    name: str

    def generate(self, request: AIRequest) -> AIResponse:
        """Return a normalized provider response for the supplied request only."""


ProviderFactory = Callable[[str], AIProviderInterface]


def get_configured_provider(
    environ: Mapping[str, str] | None = None,
    registry: Mapping[str, ProviderFactory] | None = None,
) -> AIProviderInterface:
    configuration = get_ai_configuration(environ)
    provider_name = configuration.provider
    if not provider_name:
        raise AIConfigurationError("AI provider is not configured.")

    try:
        if registry is not None:
            # An explicit registry remains authoritative, including an empty one.
            factory = registry.get(provider_name)
            if factory is None:
                raise AIConfigurationError("Configured AI provider is not supported.")
            return factory(configuration.api_key)
        if provider_name == "openai":
            # Lazy import: missing OpenAI configuration never blocks app startup.
            from .openai_provider import OpenAIProvider

            return OpenAIProvider(get_openai_configuration(environ))
        raise AIConfigurationError("Configured AI provider is not supported.")
    except AIEnvironmentError as exc:
        raise AIConfigurationError(str(exc)) from None
    except AIConfigurationError:
        raise
    except Exception:
        raise AIConfigurationError("AI provider configuration is invalid.") from None
