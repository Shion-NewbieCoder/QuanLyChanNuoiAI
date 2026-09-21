from .common import SYSTEM_PROMPT, PromptSpec


PROMPT = PromptSpec(
    version="growth-report-v1",
    system_prompt=SYSTEM_PROMPT,
    user_prompt=(
        "Explain the supplied GrowthRecord history and backend-calculated metrics exactly as supplied. "
        "Preserve every measurement date, weight and metric; do not recalculate official metrics. "
        "Describe recorded change or trend only and points deserving continued observation "
        "in a non-diagnostic way. Do not invent missing measurements."
    ),
    output_constraints=(
        "Return concise human-readable text, not JSON.",
        "Include recorded growth summary, backend metrics interpretation, points to continue monitoring, "
        "and evidence limitations when relevant.",
        "Do not forecast future weight, predict disease, diagnose or prescribe treatment; "
        "no forecasting or prediction.",
    ),
)


def build_growth_report_prompt() -> PromptSpec:
    return PROMPT
