from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.filters import BaseFilterBackend


class ExactFieldFilterBackend(BaseFilterBackend):
    """Apply exact matches for the model fields explicitly allowed by a view."""

    def filter_queryset(self, request, queryset, view):
        filters = {}
        errors = {}

        for field_name in getattr(view, "exact_filter_fields", ()):
            if field_name not in request.query_params:
                continue

            raw_value = request.query_params.get(field_name)
            if raw_value == "":
                continue

            model_field = queryset.model._meta.get_field(field_name)
            value_field = model_field.target_field if model_field.is_relation else model_field
            try:
                filters[field_name] = value_field.to_python(raw_value)
            except (DjangoValidationError, TypeError, ValueError):
                errors[field_name] = ["Invalid value."]

        if errors:
            raise ValidationError(errors)

        return queryset.filter(**filters)
