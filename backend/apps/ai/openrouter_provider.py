"""OpenRouter via the existing Responses transport; live compatibility still needs smoke testing."""

from openai import OpenAI

from config.environment import OpenRouterConfiguration

from .openai_provider import OpenAIProvider
from .providers import AIConfigurationError


class OpenRouterProvider(OpenAIProvider):
    """Reuse serialization, size guard, normalization and SDK error mapping unchanged.

    Only client configuration and the provider marker differ. Keeping store=False
    and truncation=disabled is intentional; offline tests cannot prove endpoint
    acceptance of these parameters for the selected free model.
    """

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
