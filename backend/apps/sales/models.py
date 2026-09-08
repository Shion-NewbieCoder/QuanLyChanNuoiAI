from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class SaleRecord(models.Model):
    target = models.ForeignKey(
        "herds.Herd",
        on_delete=models.PROTECT,
        related_name="sale_records",
    )
    sale_date = models.DateField()
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-sale_date"]

    def __str__(self):
        return f"{self.target} - {self.sale_date}"
