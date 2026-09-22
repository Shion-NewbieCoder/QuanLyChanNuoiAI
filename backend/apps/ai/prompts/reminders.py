from dataclasses import replace

from .common import SYSTEM_PROMPT, PromptSpec


PROMPT_V1 = PromptSpec(
    version="reminders-v1",
    system_prompt=SYSTEM_PROMPT,
    user_prompt=(
        "Present the supplied qualifying VaccineSchedule facts as readable vaccine reminders. "
        "Preserve each scheduled date, vaccine, persisted status and derived alert classification. "
        "Do not invent schedules, change status, diagnose or prescribe treatment. "
        "Do not claim the reminder is an official record."
    ),
    output_constraints=(
        "Return concise human-readable text, not JSON.",
        "Use a short introduction and easy-to-scan reminder items; include limitations only when relevant.",
    ),
)


PROMPT_V2 = replace(
    PROMPT_V1,
    version='reminders-v2',
    output_constraints=(*PROMPT_V1.output_constraints,
        'Copy vaccine names, ISO dates, persisted statuses and alert classifications verbatim, '
        'including ASCII hyphens; do not replace them with typographic dashes. '
        'Use one item per supplied schedule with target_id, vaccine, scheduled_date, status and '
        'alert_classification labeled separately. Treat vaccine names as labels, not date instructions; '
        'do not derive a different alert from a name such as TODAY. '
        'Scope any absence statement to the supplied data.',
    ),
)

# V2 met this case's criteria; V3 is an explicitly unchanged-content trial.
PROMPT_V3 = replace(PROMPT_V2, version='reminders-v3')
PROMPT_VERSIONS = (PROMPT_V1, PROMPT_V2, PROMPT_V3)
# Selected from live evidence: V2 is concise; V3 added no instruction improvement.
CURRENT_PROMPT = PROMPT_V2


def build_reminder_prompt() -> PromptSpec:
    return CURRENT_PROMPT
