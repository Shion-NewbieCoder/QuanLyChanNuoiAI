"""HTML form adapter. All writes pass through existing API serializers."""
from django import forms
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models
from rest_framework.exceptions import ValidationError as ApiValidationError

from apps.herds.appearance import AVATAR_CHOICES

from .resources import LABELS


def add_validation_errors(form, errors):
    if isinstance(errors, DjangoValidationError):
        errors = errors.message_dict if hasattr(errors, "message_dict") else errors.messages
    if not isinstance(errors, dict):
        errors = {"__all__": errors}
    for name, values in errors.items():
        field = name if name in form.fields else None
        if not isinstance(values, (list, tuple)):
            values = [values]
        for value in values:
            form.add_error(field, str(value))


def style_form(form):
    for field in form.fields.values():
        field.widget.attrs["class"] = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
        if isinstance(field.widget, forms.Textarea):
            field.widget.attrs["rows"] = 3
    return form


class ResourceForm(forms.Form):
    def __init__(self, resource, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.resource = resource
        self.instance = instance
        self.validated_serializer = None
        contract = resource.viewset.serializer_class()
        for name in resource.fields:
            model_field = resource.model._meta.get_field(name)
            field = model_field.formfield()
            field.label = LABELS[name]
            field.required = contract.fields[name].required
            if isinstance(model_field, models.DateTimeField):
                field.widget = forms.DateTimeInput(format="%Y-%m-%dT%H:%M:%S", attrs={"type": "datetime-local", "step": "1"})
            elif isinstance(model_field, models.DateField):
                field.widget = forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"})
            if name in ("status", "management_mode", "animal_type", "event_type") and not model_field.choices:
                field.help_text = "Nhập theo cách ghi nhận của nông trại; không có danh mục bắt buộc."
            self.fields[name] = field
            if instance is not None:
                self.initial[name] = getattr(instance, model_field.attname)
            elif model_field.has_default():
                self.initial[name] = model_field.get_default()
        style_form(self)
        if resource.slug in ("herds", "animals", "animal-groups"):
            self.fields["avatar"] = forms.ChoiceField(
                label="Hình đại diện", choices=AVATAR_CHOICES, required=False,
                widget=AvatarPicker,
                help_text="Chọn hình minh họa cho bản ghi này, hoặc để hệ thống chọn theo loại vật nuôi.",
            )
            self.initial["avatar"] = instance.avatar if instance is not None else ""

    def clean(self):
        cleaned = super().clean()
        if self.errors:
            return cleaned
        payload = {name: value.pk if isinstance(value, models.Model) else value
                   for name, value in cleaned.items() if name in self.resource.fields}
        self.validated_serializer = self.resource.viewset.serializer_class(instance=self.instance, data=payload)
        try:
            self.validated_serializer.is_valid(raise_exception=True)
        except ApiValidationError as exc:
            add_validation_errors(self, exc.detail)
        except DjangoValidationError as exc:
            add_validation_errors(self, exc)
        return cleaned

    def save(self):
        instance = self.validated_serializer.save()
        if "avatar" in self.fields and self.add_prefix("avatar") in self.data:
            instance.avatar = self.cleaned_data["avatar"]
            instance.save(update_fields=["avatar"])
        return instance


class AvatarPicker(forms.RadioSelect):
    template_name = "dashboard/widgets/avatar_picker.html"


class AIFeatureForm(forms.Form):
    def __init__(self, feature, *args, **kwargs):
        from apps.herds.models import Herd
        super().__init__(*args, **kwargs)
        if feature == "reminders":
            self.fields["scope"] = forms.ChoiceField(label="Phạm vi", choices=[("all", "Tất cả đàn"), ("herd", "Một đàn")])
            self.fields["target_id"] = forms.ModelChoiceField(label="Đàn cần nhắc", queryset=Herd.objects.all(), required=False,
                help_text="Chỉ chọn đàn khi phạm vi là Một đàn.")
        else:
            self.fields["herd_id"] = forms.ModelChoiceField(label="Chọn đàn", queryset=Herd.objects.all(), empty_label="Chưa có đàn" if not Herd.objects.exists() else "Chọn một đàn")
        if feature != "herd_summary":
            for name, label in (("start_date", "Từ ngày"), ("end_date", "Đến ngày")):
                self.fields[name] = forms.DateField(label=label, required=False, widget=forms.DateInput(attrs={"type": "date"}))
        style_form(self)

    def payload(self):
        return {name: value.pk if isinstance(value, models.Model) else value
                for name, value in self.cleaned_data.items() if value is not None}
