from django.db import models


class ReproductionRecord(models.Model):
    target = models.ForeignKey(
        "herds.Herd",
        on_delete=models.PROTECT,
        related_name="reproduction_records",
    )
    event_date = models.DateField()
    event_type = models.CharField(max_length=200)
    result = models.CharField(max_length=200, blank=True, default="")
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-event_date"]

    def __str__(self):
        return f"{self.target} - {self.event_date}"
