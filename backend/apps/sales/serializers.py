from decimal import Decimal

from rest_framework import serializers

from apps.domain_validation import validate_sale_record

from .models import SaleRecord


class SaleRecordSerializer(serializers.ModelSerializer):
    quantity = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0"),
        required=False,
        allow_null=True,
    )
    weight = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0"),
        required=False,
        allow_null=True,
    )
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0"),
    )

    class Meta:
        model = SaleRecord
        fields = ["id", "target", "sale_date", "quantity", "weight", "amount", "notes"]

    def validate(self, attrs):
        instance = self.instance or SaleRecord()
        for field_name in ["target", "sale_date", "quantity", "weight", "amount", "notes"]:
            if field_name in attrs:
                setattr(instance, field_name, attrs[field_name])
        validate_sale_record(instance)
        return attrs
