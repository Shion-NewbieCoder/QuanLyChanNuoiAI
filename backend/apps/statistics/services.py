from decimal import Decimal

from django.db.models import Avg, Count, Sum

from apps.growth.models import GrowthRecord

from .models import CostRecord, HerdLossRecord


def _decimal_text(value):
    if value is None:
        return None
    return format(value, ".2f")


def get_growth_statistics():
    aggregates = GrowthRecord.objects.aggregate(
        record_count=Count("id"),
        total_weight=Sum("weight"),
        average_weight=Avg("weight"),
    )
    return {
        "record_count": aggregates["record_count"],
        "total_weight": _decimal_text(aggregates["total_weight"] or Decimal("0")),
        "average_weight": _decimal_text(aggregates["average_weight"]),
    }


def get_cost_statistics(start_date=None, end_date=None):
    records = CostRecord.objects.all()
    if start_date is not None:
        records = records.filter(cost_date__gte=start_date)
    if end_date is not None:
        records = records.filter(cost_date__lte=end_date)

    total = records.aggregate(total=Sum("amount"))["total"] or Decimal("0")
    by_category = {
        row["category"]: _decimal_text(row["total"])
        for row in records.values("category").annotate(total=Sum("amount")).order_by("category")
    }
    return {"total_cost": _decimal_text(total), "by_category": by_category}


def get_loss_statistics(start_date=None, end_date=None):
    records = HerdLossRecord.objects.all()
    if start_date is not None:
        records = records.filter(period_start__gte=start_date)
    if end_date is not None:
        records = records.filter(period_end__lte=end_date)

    aggregates = records.aggregate(
        record_count=Count("id"),
        opening_quantity=Sum("opening_quantity"),
        lost_quantity=Sum("lost_quantity"),
    )
    opening_quantity = aggregates["opening_quantity"]
    lost_quantity = aggregates["lost_quantity"]
    loss_rate = None
    if opening_quantity:
        loss_rate = Decimal(lost_quantity) / Decimal(opening_quantity) * Decimal("100")

    return {
        "record_count": aggregates["record_count"],
        "opening_quantity": opening_quantity or 0,
        "lost_quantity": lost_quantity or 0,
        "loss_rate_percent": _decimal_text(loss_rate),
    }
