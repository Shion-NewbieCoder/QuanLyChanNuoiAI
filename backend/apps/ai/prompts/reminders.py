from .common import SYSTEM_PROMPT, PromptSpec


PROMPT = PromptSpec(
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


def build_reminder_prompt() -> PromptSpec:
    return PROMPT
