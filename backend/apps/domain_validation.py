from decimal import Decimal

from django.core.exceptions import ValidationError


class DomainValidationService:
    @staticmethod
    def validate_pen_target(pen):
        targets = [
            ("herd", pen.herd_id),
            ("animal_group", pen.animal_group_id),
            ("animal", pen.animal_id),
        ]
        populated = [(name, value) for name, value in targets if value is not None]

        if len(populated) != 1:
            raise ValidationError(
                {
                    "__all__": (
                        "Pen must have exactly one target: Herd, AnimalGroup, or Animal."
                    )
                }
            )

        for field_name, raw_value in populated:
            if raw_value is None:
                raise ValidationError({field_name: "Pen target is required."})

            field = pen._meta.get_field(field_name)
            related_model = field.remote_field.model
            if not related_model.objects.filter(pk=raw_value).exists():
                raise ValidationError({field_name: f"Invalid {field_name} reference."})

        return True

    @staticmethod
    def validate_care_log(care_log):
        if care_log.herd_id is None:
            raise ValidationError({"herd": "CareLog requires a valid Herd target."})

        herd_model = care_log._meta.get_field("herd").remote_field.model
        if not herd_model.objects.filter(pk=care_log.herd_id).exists():
            raise ValidationError({"herd": "CareLog requires a valid Herd target."})

        return True

    @staticmethod
    def validate_growth_record(record):
        if record.target_id is None:
            raise ValidationError({"target": "GrowthRecord requires a valid target."})

        target_model = record._meta.get_field("target").remote_field.model
        if not target_model.objects.filter(pk=record.target_id).exists():
            raise ValidationError({"target": "GrowthRecord requires a valid target."})

        if record.measurement_date is None:
            raise ValidationError({"measurement_date": "measurement_date is required."})

        if record.weight is None:
            raise ValidationError({"weight": "weight is required."})

        if record.weight < 0:
            raise ValidationError({"weight": "weight must be non-negative."})

        return True

    @staticmethod
    def validate_reproduction_record(record):
        if record.target_id is None:
            raise ValidationError({"target": "ReproductionRecord requires a valid Herd target."})

        target_model = record._meta.get_field("target").remote_field.model
        if not target_model.objects.filter(pk=record.target_id).exists():
            raise ValidationError({"target": "ReproductionRecord requires a valid Herd target."})

        if record.event_date is None:
            raise ValidationError({"event_date": "event_date is required."})

        if not record.event_type or not str(record.event_type).strip():
            raise ValidationError({"event_type": "event_type is required."})

        return True

    @staticmethod
    def validate_sale_record(record):
        if record.target_id is None:
            raise ValidationError({"target": "SaleRecord requires a valid Herd target."})

        target_model = record._meta.get_field("target").remote_field.model
        if not target_model.objects.filter(pk=record.target_id).exists():
            raise ValidationError({"target": "SaleRecord requires a valid Herd target."})

        if record.sale_date is None:
            raise ValidationError({"sale_date": "sale_date is required."})

        if record.amount is None:
            raise ValidationError({"amount": "amount is required."})

        if record.amount < 0:
            raise ValidationError({"amount": "amount must be non-negative."})

        if record.quantity is not None and record.quantity < 0:
            raise ValidationError({"quantity": "quantity must be non-negative when provided."})

        if record.weight is not None and record.weight < 0:
            raise ValidationError({"weight": "weight must be non-negative when provided."})

        return True

    @staticmethod
    def derive_sale_revenue(record):
        DomainValidationService.validate_sale_record(record)
        return record.amount

    @staticmethod
    def derive_sales_revenue(records):
        return sum(
            (DomainValidationService.derive_sale_revenue(record) for record in records),
            Decimal("0"),
        )

    @staticmethod
    def validate_vaccine_schedule(schedule):
        if schedule.target_id is None:
            raise ValidationError({"target": "VaccineSchedule requires a valid Herd target."})

        target_model = schedule._meta.get_field("target").remote_field.model
        if not target_model.objects.filter(pk=schedule.target_id).exists():
            raise ValidationError({"target": "VaccineSchedule requires a valid Herd target."})

        if not schedule.vaccine or not str(schedule.vaccine).strip():
            raise ValidationError({"vaccine": "vaccine is required."})

        if schedule.scheduled_date is None:
            raise ValidationError({"scheduled_date": "scheduled_date is required."})

        valid_statuses = {
            choice[0] for choice in schedule.Status.choices
        }
        if schedule.status not in valid_statuses:
            raise ValidationError({"status": "status must be one of the approved vaccine schedule states."})

        return True

    @staticmethod
    def validate_herd_loss_record(record):
        if record.herd_id is None:
            raise ValidationError({"herd": "HerdLossRecord requires a valid Herd target."})
        herd_model = record._meta.get_field("herd").remote_field.model
        if not herd_model.objects.filter(pk=record.herd_id).exists():
            raise ValidationError({"herd": "HerdLossRecord requires a valid Herd target."})
        if record.period_start is None or record.period_end is None:
            raise ValidationError({"period_start": "Reporting period is required."})
        if record.period_end < record.period_start:
            raise ValidationError({"period_end": "period_end must be on or after period_start."})
        if record.opening_quantity is None or record.opening_quantity <= 0:
            raise ValidationError({"opening_quantity": "opening_quantity must be greater than zero."})
        if record.lost_quantity is None or record.lost_quantity < 0:
            raise ValidationError({"lost_quantity": "lost_quantity must be non-negative."})
        if record.lost_quantity > record.opening_quantity:
            raise ValidationError({"lost_quantity": "lost_quantity cannot exceed opening_quantity."})
        return True

    @staticmethod
    def validate_cost_record(record):
        if record.herd_id is None:
            raise ValidationError({"herd": "CostRecord requires a valid Herd target."})
        herd_model = record._meta.get_field("herd").remote_field.model
        if not herd_model.objects.filter(pk=record.herd_id).exists():
            raise ValidationError({"herd": "CostRecord requires a valid Herd target."})
        if record.cost_date is None:
            raise ValidationError({"cost_date": "cost_date is required."})
        valid_categories = {choice[0] for choice in record.Category.choices}
        if record.category not in valid_categories:
            raise ValidationError({"category": "category must be an approved cost category."})
        if record.amount is None or record.amount < 0:
            raise ValidationError({"amount": "amount must be non-negative."})
        return True


def validate_pen_target(pen):
    return DomainValidationService.validate_pen_target(pen)


def validate_care_log(care_log):
    return DomainValidationService.validate_care_log(care_log)


def validate_growth_record(record):
    return DomainValidationService.validate_growth_record(record)


def validate_reproduction_record(record):
    return DomainValidationService.validate_reproduction_record(record)


def validate_sale_record(record):
    return DomainValidationService.validate_sale_record(record)


def derive_sale_revenue(record):
    return DomainValidationService.derive_sale_revenue(record)


def derive_sales_revenue(records):
    return DomainValidationService.derive_sales_revenue(records)


def validate_vaccine_schedule(schedule):
    return DomainValidationService.validate_vaccine_schedule(schedule)


def validate_herd_loss_record(record):
    return DomainValidationService.validate_herd_loss_record(record)


def validate_cost_record(record):
    return DomainValidationService.validate_cost_record(record)
