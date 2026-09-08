from dataclasses import dataclass
from typing import Callable, Mapping, Protocol

from config.environment import get_ai_configuration


class AIConfigurationError(Exception):
    """Safe error raised when an AI provider cannot be configured."""


class AIProviderError(Exception):
    """Safe provider-boundary error; provider details remain internal."""


@dataclass(frozen=True)
class AIRequest:
    prompt: str
    context: dict[str, object]


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
    if environ is None:
        configuration = get_ai_configuration()
        provider_name = configuration.provider.strip().lower()
        api_key = configuration.api_key
    else:
        provider_name = environ.get("AI_PROVIDER", "").strip().lower()
        api_key = environ.get("AI_API_KEY", "")
    if not provider_name:
        raise AIConfigurationError("AI provider is not configured.")

    providers = registry or {}
    factory = providers.get(provider_name)
    if factory is None:
        raise AIConfigurationError("Configured AI provider is not supported.")

    try:
        return factory(api_key)
    except AIConfigurationError:
        raise
    except Exception as exc:
        raise AIConfigurationError("AI provider configuration is invalid.") from exc
