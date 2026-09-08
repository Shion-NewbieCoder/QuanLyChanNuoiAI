from django.core.exceptions import ValidationError
from django.db import models


class Pen(models.Model):
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, default="")
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=50)
    herd = models.ForeignKey(
        "herds.Herd",
        on_delete=models.PROTECT,
        related_name="pens",
        null=True,
        blank=True,
    )
    animal_group = models.ForeignKey(
        "herds.AnimalGroup",
        on_delete=models.PROTECT,
        related_name="pens",
        null=True,
        blank=True,
    )
    animal = models.ForeignKey(
        "herds.Animal",
        on_delete=models.PROTECT,
        related_name="pens",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["code"]

    def clean(self):
        super().clean()
        targets = [self.herd, self.animal_group, self.animal]
        populated_targets = [target for target in targets if target is not None]

        if len(populated_targets) != 1:
            raise ValidationError(
                {
                    "__all__": (
                        "Pen must have exactly one target: Herd, AnimalGroup, or Animal."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.name}"
