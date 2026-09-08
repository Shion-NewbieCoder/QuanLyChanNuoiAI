import logging

from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.views import set_rollback


logger = logging.getLogger(__name__)


def _error_response(error_code, message, status_code, field_errors=None):
    payload = {"error_code": error_code, "message": message}
    if field_errors is not None:
        payload["field_errors"] = field_errors
    return Response(payload, status=status_code)


def api_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is None:
        request = context.get("request")
        user = getattr(request, "user", None)
        user_id = getattr(user, "pk", None) if getattr(user, "is_authenticated", False) else None
        logger.exception(
            "Unexpected API exception path=%s user_id=%s exception_category=%s",
            getattr(request, "path", ""),
            user_id,
            exc.__class__.__name__,
        )
        set_rollback()
        return _error_response(
            "internal_error",
            "An unexpected server error occurred.",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, exceptions.ValidationError):
        return _error_response(
            "validation_error",
            "Validation failed.",
            response.status_code,
            response.data,
        )
    if isinstance(exc, exceptions.NotAuthenticated):
        return _error_response(
            "authentication_required",
            "Authentication credentials were not provided.",
            response.status_code,
        )
    if isinstance(exc, exceptions.AuthenticationFailed):
        return _error_response(
            "authentication_failed",
            "Authentication failed.",
            response.status_code,
        )
    if isinstance(exc, exceptions.PermissionDenied):
        return _error_response("permission_denied", "Permission denied.", response.status_code)
    if isinstance(exc, exceptions.NotFound) or response.status_code == status.HTTP_404_NOT_FOUND:
        return _error_response("not_found", "Resource not found.", response.status_code)

    error_code = getattr(exc, "default_code", "api_error")
    detail = response.data.get("detail") if isinstance(response.data, dict) else response.data
    return _error_response(error_code, str(detail), response.status_code)
