import logging

from apps.users.roles import ROLE_MANAGEMENT, ROLE_TECHNICIAN, get_user_role

from .providers import AIProviderError, AIProviderInterface, AIRequest, AIResponse
from .safety import AIOutputValidationError, validate_and_normalize_output


logger = logging.getLogger(__name__)
AI_ALLOWED_ROLES = {ROLE_MANAGEMENT, ROLE_TECHNICIAN}


class AIAccessDenied(Exception):
    """Internal authorization boundary for future AI entry points."""


class AIInvocationError(Exception):
    """Safe normalized failure for callers; never contains provider credentials."""


class AIOrchestrator:
    """The sole application seam between approved data and an AI provider adapter."""

    def __init__(self, provider: AIProviderInterface):
        self.provider = provider

    def run(self, user, prompt: str, context: dict[str, object]) -> AIResponse:
        if get_user_role(user) not in AI_ALLOWED_ROLES:
            raise AIAccessDenied("AI access is not permitted.")

        request = AIRequest(prompt=prompt, context=dict(context))
        try:
            response = self.provider.generate(request)
        except AIProviderError as exc:
            logger.warning(
                "AI provider invocation failed provider=%s category=%s",
                getattr(self.provider, "name", "unknown"),
                exc.__class__.__name__,
            )
            raise AIInvocationError("AI provider is unavailable.") from None
        except Exception as exc:
            logger.warning(
                "AI provider invocation failed provider=%s category=%s",
                getattr(self.provider, "name", "unknown"),
                exc.__class__.__name__,
            )
            raise AIInvocationError("AI provider is unavailable.") from None

        try:
            return validate_and_normalize_output(response)
        except AIOutputValidationError as exc:
            logger.warning(
                "AI provider output rejected provider=%s category=%s",
                getattr(self.provider, "name", "unknown"),
                exc.__class__.__name__,
            )
            raise AIInvocationError("AI provider returned an invalid response.") from None
