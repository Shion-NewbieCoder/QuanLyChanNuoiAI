import logging

from apps.users.roles import ROLE_MANAGEMENT, ROLE_TECHNICIAN, get_user_role

from .providers import AIErrorCategory, AIProviderError, AIProviderInterface, AIRequest, AIResponse
from .prompts import PromptSpec
from .safety import AIOutputValidationError, validate_and_normalize_output


logger = logging.getLogger(__name__)
AI_ALLOWED_ROLES = {ROLE_MANAGEMENT, ROLE_TECHNICIAN}


class AIAccessDenied(Exception):
    """Internal authorization boundary for future AI entry points."""


class AIInvocationError(Exception):
    """Safe normalized failure for callers; never contains provider credentials."""

    def __init__(self, message, *, category=AIErrorCategory.PROVIDER_FAILURE):
        super().__init__(message)
        self.category = AIErrorCategory(category)


class AIOrchestrator:
    """The sole application seam between approved data and an AI provider adapter."""

    def __init__(self, provider: AIProviderInterface):
        self.provider = provider

    def run(self, user, prompt: PromptSpec, context: dict[str, object]) -> AIResponse:
        if get_user_role(user) not in AI_ALLOWED_ROLES:
            raise AIAccessDenied("AI access is not permitted.")

        request = AIRequest(
            system_prompt=prompt.system_prompt,
            user_prompt=prompt.user_prompt,
            context=dict(context),
            prompt_version=prompt.version,
            output_constraints=prompt.output_constraints,
        )
        try:
            response = self.provider.generate(request)
        except AIProviderError as exc:
            logger.warning(
                "AI provider invocation failed provider=%s category=%s",
                getattr(self.provider, "name", "unknown"),
                exc.category.value,
            )
            raise AIInvocationError("AI provider is unavailable.", category=exc.category) from None
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
            raise AIInvocationError(
                "AI provider returned an invalid response.", category=AIErrorCategory.INVALID_RESPONSE
            ) from None
