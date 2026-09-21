from dataclasses import replace

from .providers import AIResponse


SAFETY_NOTICE = (
    "AI chỉ cung cấp gợi ý tham khảo và không thay thế bác sĩ thú y/"
    "kỹ sư chăn nuôi."
)

class AIOutputValidationError(Exception):
    """Raised internally when a provider response is not safe to present."""


def validate_and_normalize_output(response: object) -> AIResponse:
    if not isinstance(response, AIResponse):
        raise AIOutputValidationError("Provider response has an invalid structure.")
    if not isinstance(response.text, str) or not response.text.strip():
        raise AIOutputValidationError("Provider response has no content.")
    if not isinstance(response.provider, str) or not response.provider.strip():
        raise AIOutputValidationError("Provider response has no provider marker.")
    return replace(response, text=response.text.strip(), provider=response.provider.strip())


def with_safety_notice(feature_notice: str = "") -> str:
    notice = feature_notice.strip()
    if not notice:
        return SAFETY_NOTICE
    if SAFETY_NOTICE in notice:
        return notice
    return f"{notice} {SAFETY_NOTICE}"
