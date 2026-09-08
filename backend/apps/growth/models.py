from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class GrowthRecord(models.Model):
    target = models.ForeignKey(
        "herds.Herd",
        on_delete=models.PROTECT,
        related_name="growth_records",
    )
    measurement_date = models.DateField()
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-measurement_date"]

    def __str__(self):
        return f"{self.target} - {self.measurement_date}"
