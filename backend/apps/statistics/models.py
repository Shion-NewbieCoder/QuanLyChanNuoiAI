from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class HerdLossRecord(models.Model):
    herd = models.ForeignKey(
        "herds.Herd",
        on_delete=models.PROTECT,
        related_name="loss_records",
    )
    period_start = models.DateField()
    period_end = models.DateField()
    opening_quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    lost_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["period_start", "period_end"]

    def clean(self):
        super().clean()
        from apps.domain_validation import validate_herd_loss_record

        validate_herd_loss_record(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class CostRecord(models.Model):
    class Category(models.TextChoices):
        FEED = "feed", "Feed"
        MEDICINE = "medicine", "Medicine"
        VACCINE = "vaccine", "Vaccine"
        CARE = "care", "Care"
        OTHER = "other", "Other"

    herd = models.ForeignKey(
        "herds.Herd",
        on_delete=models.PROTECT,
        related_name="cost_records",
    )
    cost_date = models.DateField()
    category = models.CharField(max_length=20, choices=Category.choices)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["cost_date", "category"]

    def clean(self):
        super().clean()
        from apps.domain_validation import validate_cost_record

        validate_cost_record(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
