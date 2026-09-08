from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class CareLog(models.Model):
    herd = models.ForeignKey(
        "herds.Herd",
        on_delete=models.PROTECT,
        related_name="care_logs",
    )
    recorded_at = models.DateTimeField()
    activity = models.CharField(max_length=200)
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-recorded_at"]


class FeedRecord(models.Model):
    herd = models.ForeignKey(
        "herds.Herd",
        on_delete=models.PROTECT,
        related_name="feed_records",
    )
    recorded_at = models.DateTimeField()
    feed_type = models.CharField(max_length=200)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-recorded_at"]


class MedicineRecord(models.Model):
    herd = models.ForeignKey(
        "herds.Herd",
        on_delete=models.PROTECT,
        related_name="medicine_records",
    )
    recorded_at = models.DateTimeField()
    medicine = models.CharField(max_length=200)
    dose = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-recorded_at"]
