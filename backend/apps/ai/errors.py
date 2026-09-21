"""Shared API/HTML presentation contract. Never render exception text or payloads."""

from dataclasses import dataclass

from .providers import AIError, AIErrorCategory


@dataclass(frozen=True)
class PublicAIError:
    code: str
    message: str
    status_code: int


CONFIGURATION = PublicAIError(
    "ai_configuration_unavailable", "AI chưa được cấu hình hoặc cấu hình không hợp lệ.", 503,
)
PROVIDER_FAILURE = PublicAIError(
    "ai_provider_failure", "Không thể kết nối tới dịch vụ AI. Vui lòng thử lại sau.", 502,
)
PUBLIC_AI_ERRORS = {
    AIErrorCategory.CONFIGURATION: CONFIGURATION,
    AIErrorCategory.AUTHENTICATION: CONFIGURATION,
    AIErrorCategory.CONNECTION: PROVIDER_FAILURE,
    AIErrorCategory.PROVIDER_FAILURE: PROVIDER_FAILURE,
    AIErrorCategory.INPUT_TOO_LARGE: PublicAIError(
        "ai_input_too_large", "Dữ liệu quá lớn để AI xử lý trong một lần. Vui lòng thu hẹp phạm vi dữ liệu.", 413,
    ),
    AIErrorCategory.RATE_LIMIT: PublicAIError(
        "ai_rate_limit", "Dịch vụ AI đang giới hạn yêu cầu. Vui lòng thử lại sau.", 429,
    ),
    AIErrorCategory.TIMEOUT: PublicAIError(
        "ai_timeout", "Dịch vụ AI phản hồi quá lâu. Vui lòng thử lại.", 504,
    ),
    AIErrorCategory.INVALID_RESPONSE: PublicAIError(
        "ai_invalid_response", "AI trả về kết quả không hợp lệ. Vui lòng thử lại.", 502,
    ),
    # The existing category covers invalid configured models/provider requests.
    AIErrorCategory.INVALID_REQUEST: PublicAIError(
        "ai_invalid_model", "Mô hình AI được cấu hình không khả dụng hoặc không hợp lệ.", 503,
    ),
}


def public_ai_error(exc: AIError) -> PublicAIError:
    return PUBLIC_AI_ERRORS[exc.category]
