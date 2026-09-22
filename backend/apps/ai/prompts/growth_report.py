from dataclasses import replace

from .common import SYSTEM_PROMPT, PromptSpec


PROMPT_V1 = PromptSpec(
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


PROMPT_V2 = replace(
    PROMPT_V1,
    version='growth-report-v2',
    output_constraints=(*PROMPT_V1.output_constraints,
        'Present every measurement and all eight backend metrics using their exact keys and '
        'supplied values, including every decimal digit; do not round, recalculate or add units '
        'that are not supplied. Describe the requested Herd recorded weights, not an individual '
        'animal. Limit interpretation to observed dates and weights. Do not add weighing protocols, '
        'feeding/health recommendations, causal explanations or expectations of sustained gain. '
        'For continued observation, identify only the limited recorded evidence; do not prescribe '
        'actions. Say records outside the supplied data are unknown, not that no such records exist.',
    ),
)

PROMPT_V3 = replace(
    PROMPT_V2,
    version='growth-report-v3',
    output_constraints=(*PROMPT_V2.output_constraints,
        'Keep measurement rows and the complete exact metric list. After them, use at most two '
        'short sentences: one describing only the recorded direction of change, and one noting '
        'the limited supplied measurements for continued observation and that other records are '
        'unknown. Do not repeat metric numbers in prose or enumerate unrelated missing domains.',
    ),
)
PROMPT_VERSIONS = (PROMPT_V1, PROMPT_V2, PROMPT_V3)
# V2 preserved exact metrics in a valid live result; V3 returned invalid_response.
CURRENT_PROMPT = PROMPT_V2


def build_growth_report_prompt() -> PromptSpec:
    return CURRENT_PROMPT
