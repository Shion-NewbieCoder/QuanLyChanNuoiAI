from .common import SYSTEM_PROMPT, PromptSpec


PROMPT = PromptSpec(
    version="herd-summary-v1",
    system_prompt=SYSTEM_PROMPT,
    user_prompt=(
        "Summarize supplied Herd, CareLog, FeedRecord, MedicineRecord, VaccineSchedule and "
        "VaccinationRecord facts only. Distinguish recorded facts from missing data. "
        "When related lists are empty, state related records are unavailable. "
        "Preserve dates, numbers and statuses. Avoid unsupported causal claims. "
        "Do not invent health conditions or infer unrecorded events; missing data is not a negative fact. "
        "Do not diagnose or prescribe treatment."
    ),
    output_constraints=(
        "Return concise human-readable text, not JSON.",
        "Give an overall factual summary, recorded care/feed/medicine/vaccine observations, "
        "and a missing or limited evidence note when relevant.",
    ),
)


def build_herd_summary_prompt() -> PromptSpec:
    return PROMPT
