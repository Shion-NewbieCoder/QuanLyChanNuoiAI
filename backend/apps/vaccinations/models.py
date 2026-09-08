from django.db import models


class VaccineSchedule(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Đã lập lịch"
        DUE = "due", "Đến hạn / cần chú ý"
        COMPLETED = "completed", "Đã thực hiện"
        CANCELLED = "cancelled", "Đã hủy"

    target = models.ForeignKey(
        "herds.Herd",
        on_delete=models.PROTECT,
        related_name="vaccine_schedules",
    )
    vaccine = models.CharField(max_length=200)
    scheduled_date = models.DateField()
    status = models.CharField(
        max_length=40,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )

    class Meta:
        ordering = ["scheduled_date", "vaccine"]

    def __str__(self):
        return f"{self.vaccine} - {self.scheduled_date}"


class VaccinationRecord(models.Model):
    schedule = models.ForeignKey(
        VaccineSchedule,
        on_delete=models.PROTECT,
        related_name="records",
    )
    actual_date = models.DateField()
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-actual_date"]

    def __str__(self):
        return f"{self.schedule.vaccine} - {self.actual_date}"
