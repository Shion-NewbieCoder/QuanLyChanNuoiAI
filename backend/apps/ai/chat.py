"""Constrained, read-only chat over explicitly selected livestock data sources."""

import re
import unicodedata

from apps.care.models import CareLog, FeedRecord, MedicineRecord
from apps.growth.models import GrowthRecord
from apps.herds.models import Animal, AnimalGroup, Herd
from apps.pens.models import Pen
from apps.reproduction.models import ReproductionRecord
from apps.sales.models import SaleRecord
from apps.domain_validation import derive_sales_revenue
from apps.statistics.models import CostRecord
from apps.statistics.services import get_cost_statistics, get_growth_statistics, get_loss_statistics
from apps.vaccinations.models import VaccinationRecord, VaccineSchedule

from .orchestrator import AIOrchestrator
from .providers import get_configured_provider
from .prompts.chat import build_chat_prompt
from .safety import with_safety_notice


MAX_RECORDS_PER_SOURCE = 10
MAX_NOTE_LENGTH = 240
CHAT_NOTICE = with_safety_notice(
    "Câu trả lời chỉ tổng hợp dữ liệu đã ghi nhận trong hệ thống."
)
OUT_OF_SCOPE_ANSWER = (
    "Mình chỉ hỗ trợ hỏi đáp về dữ liệu chăn nuôi đã ghi nhận trong hệ thống; "
    "câu hỏi này nằm ngoài phạm vi đó hoặc yêu cầu tư vấn chuyên môn."
)

# Matching is deterministic and happens before any source query. The chat model
# cannot choose a model, field, filter, relation, or query.
SOURCE_TERMS = {
    "herds": ("dan", "vat nuoi", "loai vat nuoi", "so luong dan"),
    "animals": ("ca the", "ma ca the", "con vat"),
    "animal_groups": ("nhom vat nuoi", "nhom dan"),
    "pens": ("chuong", "chuong trai"),
    "care": ("cham soc", "nhat ky cham soc", "hoat dong cham soc"),
    "feed": ("thuc an", "cho an", "luong an"),
    "medicine": ("thuoc", "thuoc da dung", "lieu luong"),
    "vaccines": ("vaccine", "vac xin", "tiem phong", "lich tiem", "lan tiem"),
    "growth": ("tang truong", "can nang", "lan can", "khoi luong"),
    "reproduction": ("sinh san", "phoi giong", "su kien sinh san"),
    "sales": ("xuat ban", "ban vat nuoi", "doanh thu", "tien ban"),
    "statistics": ("thong ke", "chi phi", "hao hut", "ty le hao hut", "so lieu tong hop"),
}
OUT_OF_SCOPE_TERMS = (
    "gia vang", "gia bac", "thoi tiet", "du bao thoi tiet", "tin tuc", "thoi su",
    "chung khoan", "ty gia", "ket qua bong da", "chan doan", "benh", "trieu chung",
    "co benh khong", "dieu tri", "ke don", "nen dung", "nen dung thuoc", "nen tiem",
    "co nen", "khuyen nghi", "loi khuyen", "phac do", "tien luong",
    "du doan", "du bao",
)
UNSAFE_ANSWER_TERMS = (
    "chan doan", "dieu tri", "ke don", "nen dung", "nen tiem", "khuyen nghi",
    "loi khuyen", "phac do", "tien luong", "du doan", "du bao",
)
SOURCE_LABELS = {
    "herds": "đàn vật nuôi",
    "animals": "cá thể",
    "animal_groups": "nhóm vật nuôi",
    "pens": "chuồng trại",
    "care": "chăm sóc",
    "feed": "thức ăn",
    "medicine": "thuốc đã ghi nhận",
    "vaccines": "vaccine và lần tiêm",
    "growth": "tăng trưởng",
    "reproduction": "sinh sản",
    "sales": "xuất bán",
    "statistics": "thống kê",
}


def _normalize_question(question):
    value = unicodedata.normalize("NFD", question.casefold())
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    value = value.replace("đ", "d")
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def select_chat_sources(question):
    normalized = _normalize_question(question)
    padded = f" {normalized} "
    if any(f" {term} " in padded for term in OUT_OF_SCOPE_TERMS):
        return ()
    selected = tuple(
        source for source, terms in SOURCE_TERMS.items()
        if any(f" {unicodedata.normalize('NFD', term).encode('ascii', 'ignore').decode().casefold()} " in padded
               for term in terms)
    )
    # Avoid turning a general or mixed unsupported request into a broad scan.
    if not selected or len(selected) > 3:
        return ()
    return selected


def _answer_requests_professional_advice(answer):
    normalized = _normalize_question(answer)
    padded = f" {normalized} "
    return any(f" {term} " in padded for term in UNSAFE_ANSWER_TERMS)


def _limited(queryset, fields, ordering):
    rows = queryset.order_by(*ordering).values(*fields)[:MAX_RECORDS_PER_SOURCE]
    return [
        {key: value.isoformat() if hasattr(value, "isoformat") else value
         for key, value in row.items()}
        for row in rows
    ]


def collect_chat_facts(sources):
    """Run only fixed projections for allowlisted source names."""
    facts = {}
    collectors = {
        "herds": lambda: _limited(Herd.objects.all(),
            ("code", "name", "animal_type", "management_mode", "quantity", "status"), ("code",)),
        "animals": lambda: _limited(Animal.objects.select_related("herd"),
            ("code", "herd__code", "status"), ("code",)),
        "animal_groups": lambda: _limited(AnimalGroup.objects.select_related("herd"),
            ("code", "name", "herd__code", "quantity", "status"), ("code",)),
        "pens": lambda: _limited(Pen.objects.select_related("herd", "animal_group", "animal"),
            ("code", "name", "location", "status", "herd__code", "animal_group__code", "animal__code"), ("code",)),
        "care": lambda: _limited(CareLog.objects.select_related("herd"),
            ("herd__code", "recorded_at", "activity", "notes"), ("-recorded_at", "pk")),
        "feed": lambda: _limited(FeedRecord.objects.select_related("herd"),
            ("herd__code", "recorded_at", "feed_type", "quantity"), ("-recorded_at", "pk")),
        "medicine": lambda: _limited(MedicineRecord.objects.select_related("herd"),
            ("herd__code", "recorded_at", "medicine", "dose"), ("-recorded_at", "pk")),
        "vaccines": lambda: (
            [{"record_type": "schedule", **row} for row in _limited(
                VaccineSchedule.objects.select_related("target"),
                ("target__code", "vaccine", "scheduled_date", "status"), ("-scheduled_date", "pk"),
            )]
            + [{"record_type": "vaccination", **row} for row in _limited(
                VaccinationRecord.objects.select_related("schedule__target"),
                ("schedule__target__code", "schedule__vaccine", "actual_date"), ("-actual_date", "pk"),
            )]
        ),
        "growth": lambda: _limited(GrowthRecord.objects.select_related("target"),
            ("target__code", "measurement_date", "weight"), ("-measurement_date", "pk")),
        "reproduction": lambda: _limited(ReproductionRecord.objects.select_related("target"),
            ("target__code", "event_date", "event_type", "result"), ("-event_date", "pk")),
        "sales": lambda: _limited(SaleRecord.objects.select_related("target"),
            ("target__code", "sale_date", "quantity", "weight", "amount"), ("-sale_date", "pk")),
        "statistics": lambda: {
            "growth": get_growth_statistics(),
            "cost": {**get_cost_statistics(), "record_count": CostRecord.objects.count()},
            "loss": get_loss_statistics(),
            "sales": {
                "record_count": SaleRecord.objects.count(),
                "revenue_total": format(derive_sales_revenue(SaleRecord.objects.all()), ".2f"),
            },
        },
    }
    for source in sources:
        facts[source] = collectors[source]()
        if source == "care":
            for row in facts[source]:
                row["notes_truncated"] = len(row["notes"]) > MAX_NOTE_LENGTH
                row["notes"] = row["notes"][:MAX_NOTE_LENGTH]
    return facts


def _has_source_data(facts):
    for source, value in facts.items():
        if source == "statistics":
            if any((value["growth"]["record_count"], value["cost"]["record_count"],
                    value["loss"]["record_count"], value["sales"]["record_count"])):
                return True
        elif value:
            return True
    return False


def answer_chat_question(user, question):
    sources = select_chat_sources(question)
    if not sources:
        return {"answer": OUT_OF_SCOPE_ANSWER, "notice": CHAT_NOTICE, "source_count": 0}

    facts = collect_chat_facts(sources)
    source_count = sum(len(value) if isinstance(value, list) else
                       value["growth"]["record_count"] + value["cost"]["record_count"] +
                       value["loss"]["record_count"] + value["sales"]["record_count"]
                       for value in facts.values())
    if not _has_source_data(facts):
        labels = ", ".join(SOURCE_LABELS[source] for source in sources)
        return {
            "answer": f"Chưa có dữ liệu đã ghi nhận về {labels} trong hệ thống để trả lời câu hỏi này.",
            "notice": CHAT_NOTICE,
            "source_count": 0,
        }

    result = AIOrchestrator(get_configured_provider()).run(
        user, build_chat_prompt(),
        {"question": question, "sources": facts, "source_count": source_count},
    )
    answer = OUT_OF_SCOPE_ANSWER if _answer_requests_professional_advice(result.text) else result.text
    return {"answer": answer, "notice": CHAT_NOTICE, "source_count": source_count}
