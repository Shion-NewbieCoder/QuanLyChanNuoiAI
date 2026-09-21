from apps.care.models import CareLog, FeedRecord, MedicineRecord
from apps.herds.models import Herd
from apps.vaccinations.models import VaccinationRecord, VaccineSchedule

from .orchestrator import AIOrchestrator
from .providers import get_configured_provider
from .safety import with_safety_notice
from .prompts.herd_summary import build_herd_summary_prompt


NOTICE = with_safety_notice("AI-generated summary based on recorded herd data.")


def build_herd_summary_facts(herd):
    schedules = list(VaccineSchedule.objects.filter(target=herd))
    schedule_ids = [schedule.id for schedule in schedules]
    facts = {
        "herd": {field: getattr(herd, field) for field in ("id", "code", "name", "animal_type", "management_mode", "quantity", "status")},
        "care_logs": [{"recorded_at": item.recorded_at.isoformat(), "activity": item.activity, "notes": item.notes} for item in CareLog.objects.filter(herd=herd)],
        "feed_records": [{"recorded_at": item.recorded_at.isoformat(), "feed_type": item.feed_type, "quantity": str(item.quantity), "notes": item.notes} for item in FeedRecord.objects.filter(herd=herd)],
        "medicine_records": [{"recorded_at": item.recorded_at.isoformat(), "medicine": item.medicine, "dose": str(item.dose), "notes": item.notes} for item in MedicineRecord.objects.filter(herd=herd)],
        "vaccine_schedules": [{"vaccine": item.vaccine, "scheduled_date": item.scheduled_date.isoformat(), "status": item.status} for item in schedules],
        "vaccination_records": [{"actual_date": item.actual_date.isoformat(), "notes": item.notes} for item in VaccinationRecord.objects.filter(schedule_id__in=schedule_ids)],
    }
    source_count = sum(len(value) for key, value in facts.items() if key != "herd")
    return facts, source_count


def generate_herd_summary(user, herd_id):
    herd = Herd.objects.get(pk=herd_id)
    facts, source_count = build_herd_summary_facts(herd)
    response = AIOrchestrator(get_configured_provider()).run(user, build_herd_summary_prompt(), {"herd_summary": facts})
    return {"text": response.text, "source_count": source_count}
