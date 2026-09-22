from dataclasses import replace

from .common import SYSTEM_PROMPT, PromptSpec


PROMPT_V1 = PromptSpec(
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


PROMPT_V2 = replace(
    PROMPT_V1,
    version='herd-summary-v2',
    output_constraints=(*PROMPT_V1.output_constraints,
        'Use compact labeled sections for Herd and each supplied record category. '
        'Preserve codes, ISO timestamps/dates, quantities, doses and status tokens verbatim. '
        'Do not invent measurement units. Present vaccination records separately from schedules; '
        'do not infer a link from matching dates because no linking field is supplied. '
        'Use absence wording limited to the supplied data rather than asserting no other records '
        'or events exist. End with one concise limitation about the supplied evidence, '
        'not a checklist of unrequested medical or future-plan data.',
    ),
)

PROMPT_V3 = replace(
    PROMPT_V2,
    version='herd-summary-v3',
    output_constraints=(*PROMPT_V2.output_constraints,
        'Label each record value with its supplied field name, especially activity and notes. '
        'A DEMO label inside notes is still notes, not a record identifier. Keep one compact '
        'bullet per supplied record and the single scoped limitation; no extra interpretation.',
    ),
)
PROMPT_VERSIONS = (PROMPT_V1, PROMPT_V2, PROMPT_V3)
# Live V3 clarified source field labels without factual/safety regression.
CURRENT_PROMPT = PROMPT_V3


def build_herd_summary_prompt() -> PromptSpec:
    return CURRENT_PROMPT
