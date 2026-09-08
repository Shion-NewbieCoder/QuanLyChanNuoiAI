import json
from decimal import Decimal

from apps.growth.models import GrowthRecord
from apps.herds.models import Herd

from .orchestrator import AIOrchestrator
from .providers import get_configured_provider
from .safety import apply_prompt_boundary, with_safety_notice


SUCCESS_NOTICE = with_safety_notice("AI-generated growth report based on recorded growth data.")
INSUFFICIENT_NOTICE = with_safety_notice(
    "Insufficient growth data to generate an AI growth report."
)


def select_growth_facts(herd, start_date=None, end_date=None):
    records = GrowthRecord.objects.filter(target=herd).order_by("measurement_date", "pk")
    if start_date is not None:
        records = records.filter(measurement_date__gte=start_date)
    if end_date is not None:
        records = records.filter(measurement_date__lte=end_date)
    return [
        {
            "measurement_date": record.measurement_date.isoformat(),
            "weight": record.weight,
            "notes": record.notes,
        }
        for record in records
    ]


def calculate_growth_metrics(records):
    count = len(records)
    if count == 0:
        return {
            "record_count": 0,
            "first_measurement_date": None,
            "first_weight": None,
            "last_measurement_date": None,
            "last_weight": None,
            "absolute_change": None,
            "percent_change": None,
            "average_weight": None,
        }

    first = records[0]
    last = records[-1]
    average = sum((record["weight"] for record in records), Decimal("0")) / count
    absolute_change = last["weight"] - first["weight"] if count >= 2 else None
    percent_change = None
    if count >= 2 and first["weight"] > 0:
        percent_change = absolute_change / first["weight"] * Decimal("100")
    return {
        "record_count": count,
        "first_measurement_date": first["measurement_date"],
        "first_weight": first["weight"],
        "last_measurement_date": last["measurement_date"],
        "last_weight": last["weight"],
        "absolute_change": absolute_change,
        "percent_change": percent_change,
        "average_weight": average,
    }


def build_growth_report_prompt(facts, metrics):
    source = {"growth_records": facts, "metrics": metrics}
    return apply_prompt_boundary(
        "Write concise growth report presentation text using only SOURCE_FACTS. "
        "Preserve every date, weight, and metric exactly; do not recalculate metrics. "
        "Do not invent facts, forecast or predict future values, diagnose, or recommend treatment. "
        "State when evidence is limited. SOURCE_FACTS: "
        + json.dumps(source, ensure_ascii=False, default=str, separators=(",", ":"))
    )


def generate_growth_report(user, herd_id, start_date=None, end_date=None):
    herd = Herd.objects.get(pk=herd_id)
    facts = select_growth_facts(herd, start_date, end_date)
    metrics = calculate_growth_metrics(facts)
    if len(facts) < 2:
        return {"text": "", "source_count": len(facts), "metrics": metrics, "notice": INSUFFICIENT_NOTICE}

    context = {
        "herd": {"id": herd.id, "code": herd.code, "name": herd.name},
        "growth_records": facts,
        "metrics": metrics,
    }
    response = AIOrchestrator(get_configured_provider()).run(
        user, build_growth_report_prompt(facts, metrics), context
    )
    return {"text": response.text, "source_count": len(facts), "metrics": metrics, "notice": SUCCESS_NOTICE}
