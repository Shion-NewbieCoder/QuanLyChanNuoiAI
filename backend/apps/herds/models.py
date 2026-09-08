from django.core.validators import MinValueValidator
from django.db import models


class Herd(models.Model):
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    animal_type = models.CharField(max_length=100)
    management_mode = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    status = models.CharField(max_length=50)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Animal(models.Model):
    code = models.CharField(max_length=100)
    herd = models.ForeignKey(
        Herd,
        on_delete=models.PROTECT,
        related_name="animals",
    )
    status = models.CharField(max_length=50)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code


class AnimalGroup(models.Model):
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    herd = models.ForeignKey(
        Herd,
        on_delete=models.PROTECT,
        related_name="animal_groups",
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    status = models.CharField(max_length=50)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"
