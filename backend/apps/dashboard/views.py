import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import DatabaseError
from django.shortcuts import render

from apps.domain_validation import derive_sales_revenue
from apps.growth.models import GrowthRecord
from apps.herds.models import Herd
from apps.sales.models import SaleRecord
from apps.statistics.services import (
    get_cost_statistics,
    get_growth_statistics,
    get_loss_statistics,
)
from apps.users.permissions import ROLE_ACTIONS
from apps.users.roles import ROLE_NAMES, get_user_role
from apps.vaccinations.models import VaccineSchedule
from apps.vaccinations.serializers import get_alert_classification


logger = logging.getLogger(__name__)
ATTENTION_CLASSIFICATIONS = {"overdue", "due today", "due soon"}


def _role_can(role, resource, action="read"):
    return action in ROLE_ACTIONS.get(resource, {}).get(role, set())


def _empty_context(role):
    return {
        "effective_role": role,
        "can_view_statistics": _role_can(role, "statistics"),
        "can_use_ai": _role_can(role, "ai"),
        "herds": [],
        "total_herds": 0,
        "total_recorded_quantity": 0,
        "attention_schedules": [],
        "recent_growth_records": [],
        "recent_sales": [],
        "revenue_total": "0.00",
        "growth_statistics": None,
        "cost_statistics": None,
        "loss_statistics": None,
        "dashboard_error": None,
    }


def build_dashboard_context(role):
    context = _empty_context(role)
    herds = list(Herd.objects.all())
    schedules = VaccineSchedule.objects.select_related("target").order_by(
        "scheduled_date", "pk"
    )
    context.update(
        {
            "herds": herds,
            "total_herds": len(herds),
            "total_recorded_quantity": sum(herd.quantity for herd in herds),
            "attention_schedules": [
                {"schedule": schedule, "classification": classification}
                for schedule in schedules
                if (classification := get_alert_classification(schedule))
                in ATTENTION_CLASSIFICATIONS
            ],
            "recent_growth_records": list(
                GrowthRecord.objects.select_related("target").order_by(
                    "-measurement_date", "-pk"
                )[:5]
            ),
            "recent_sales": list(
                SaleRecord.objects.select_related("target").order_by(
                    "-sale_date", "-pk"
                )[:5]
            ),
        }
    )
    if context["can_view_statistics"]:
        context.update(
            {
                "revenue_total": format(
                    derive_sales_revenue(SaleRecord.objects.all()), ".2f"
                ),
                "growth_statistics": get_growth_statistics(),
                "cost_statistics": get_cost_statistics(),
                "loss_statistics": get_loss_statistics(),
            }
        )
    return context


@login_required
def dashboard(request):
    role = get_user_role(request.user)
    if role not in ROLE_NAMES:
        raise PermissionDenied("A recognized role is required.")
    try:
        context = build_dashboard_context(role)
    except DatabaseError:
        logger.exception(
            "Dashboard data could not be loaded user_id=%s",
            request.user.pk,
        )
        context = _empty_context(role)
        context["dashboard_error"] = (
            "Không thể tải dữ liệu tổng quan. Vui lòng thử lại."
        )
    if context["can_use_ai"] and not context["dashboard_error"]:
        from .ui import ai_cards
        context["ai_cards"] = ai_cards()
    return render(request, "dashboard/dashboard.html", context)
