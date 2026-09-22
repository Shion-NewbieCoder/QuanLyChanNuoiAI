# KT3 AI Prompt Experiments

## 1. Purpose

TSK-KT3-07: đánh giá học thuật ba feature hiện hữu, fixed model, V1 → V2 → V3. Không benchmarking production, không chấm điểm số, không chứng nhận chính xác thú y. Nhận xét dưới đây do coding assistant phân tích output thực tế; phê duyệt sau review của sinh viên được ghi riêng tại mục 18.

## 2. Evaluation Environment

Baseline: `fafbdd1a7019ff1e2af71c7159946b8b796eec95`. Ngày đánh giá: 2026-09-22, Asia/Ho_Chi_Minh. V1 và hai output V2 đầu được khôi phục từ terminal transcript của phiên trước; không gọi lại.
Django production services, PromptSpec, AIOrchestrator, OpenRouterProvider và normalization hiện hữu. Database SQLite mở bằng URI mode=ro và PRAGMA query_only=ON cho mỗi lượt inference.
SHA-256 database baseline: `f6a29349a8827ff023d143e4dfee9f2839e736c05e4a253fffccb74b063b5d18`.
Safe configuration check: AI_PROVIDER=openrouter; model như mục 3; OPENROUTER_API_KEY_PRESENT=true; DJANGO_SECRET_KEY_PRESENT=true. Không lưu giá trị secret.

## 3. Provider and Fixed Model

Provider: OpenRouter
Model: nvidia/nemotron-3-ultra-550b-a55b:free
Base URL: https://openrouter.ai/api/v1
Responses API, store=False, truncation="disabled", max_retries=0, input guard=65,536 bytes. Không tools, routing hoặc fallback.
Amendment 08 supersedes phần primary-provider của 07; optional OpenAI adapter không đổi.

## 4. Methodology

Mỗi feature dùng cùng nguồn, cùng filter và cùng backend metrics qua các vòng. Không seed/update/delete business records. Snapshot database và ngày hệ thống được kiểm tra trước mỗi vòng để không đổi derived classifications.
Chỉ thay prompt/output constraints sau khi xem output vòng trước. Một kết quả/feature/version; stochastic wording không là test expectation.
Đánh giá mô tả: grounding, completeness, clarity/readability, conciseness, safety/scope, uncertainty, format. Giữ output sai trong evidence; không sửa output để làm đẹp kết quả.
OpenAI Docs hỗ trợ separation instructions/context và evaluation có kiểm soát; không được dùng để khẳng định OpenRouter/model này tuân thủ:
[Prompt engineering](https://developers.openai.com/api/docs/guides/prompt-engineering).

### Controlled recovery deviation and budget

Original Growth V2 invocation started at 2026-09-22T06:58:55.799466+00:00, but its final result was lost because the previous Codex session terminated. No claim is made about whether that invocation reached the provider successfully or completed. It is conservatively counted against the live-call budget.
The student explicitly authorized exactly one replacement Growth V2 evaluation. It started at 2026-09-22T14:25:00.333957+00:00 and succeeded; its complete output is recorded in section 9.
Final budget: 3 V1 + 2 confirmed V2 + 1 unknown original Growth V2 + 1 replacement Growth V2 + 3 V3 attempts = 10/10 consumed/reserved. Eight successful results are available, one original result is unknown, and Growth V3 failed with invalid_response. No slots remain.
Optional safety live call is omitted to preserve the hard maximum. No repeated Reminder V2, Herd Summary V2 or V1 calls.

## 5. Stable Evaluation Cases

All cases use existing Herd id=1, code=DEMO-HERD-001, name=Đàn bò demo chính. Existing authorized demo manager is used only for RBAC; user/auth/group/session data are not prompt context.
All free text inspected: synthetic DEMO labels and livestock demo notes only.

| Case | Approved source snapshot | source_count |
|---|---|---|
| A Reminder | scope=herd, target_id=1, no dates; three qualifying schedules below | 3 |
| B Herd Summary | Herd facts + CareLog 2, FeedRecord 2, MedicineRecord 2, VaccineSchedule 4, VaccinationRecord 1; Herd itself excluded from count | 11 |
| C Growth Report | Three measurements below, no dates; only Herd id/code/name, GrowthRecord measurement_date/weight/notes and backend metrics | 3 |

Reminder source:
- DEMO-VACCINE-OVERDUE, 2026-09-02, status=due, alert_classification=overdue.
- DEMO-VACCINE-TODAY, 2026-09-09, status=due, alert_classification=overdue.
- DEMO-VACCINE-FUTURE, 2026-10-09, status=scheduled, alert_classification=scheduled-not-yet-due.
- target_id=1 for all. TODAY is a historical seed label, not the current date classification. Completed schedule excluded by existing service.

Summary source: Herd animal_type=bò, management_mode=group, quantity=100, status=active.
- Care: 2026-09-04T01:00:00+00:00, activity=DEMO-CARE-002, notes=Vệ sinh khu chăn nuôi; 2026-08-28T01:00:00+00:00, activity=DEMO-CARE-001, notes=Kiểm tra tổng quát.
- Feed: 2026-09-06T02:00:00+00:00, feed_type=DEMO-FEED-002, quantity=180.00, notes=Khẩu phần thức ăn hỗn hợp; 2026-08-30T02:00:00+00:00, feed_type=DEMO-FEED-001, quantity=250.00, notes=Khẩu phần cỏ khô.
- Medicine: 2026-09-07T03:00:00+00:00, medicine=DEMO-MEDICINE-002, dose=3.00, notes=Thuốc demo theo dõi; 2026-08-31T03:00:00+00:00, medicine=DEMO-MEDICINE-001, dose=5.00, notes=Vitamin bổ sung.
- Vaccine: all three schedules above (without derived classification/target_id in summary context), plus DEMO-VACCINE-COMPLETED, 2026-08-10, completed.
- Vaccination: actual_date=2026-08-10, notes=DEMO-VACCINATION-001; no linking field sent.
- No Growth/Reproduction/Sale/Cost/Loss/statistics/reminder output/user/auth/group data supplied to summary.

Growth source: 2026-07-11 weight=100.00 notes=DEMO-GROWTH-001; 2026-08-10 weight=112.00 notes=DEMO-GROWTH-002; 2026-09-09 weight=125.00 notes=DEMO-GROWTH-003.
No unit field is supplied to AI. Exact backend metrics for every Growth round (Decimal serialized as strings, not rounded):

```json
{
  "record_count": 3,
  "first_measurement_date": "2026-07-11",
  "first_weight": "100.00",
  "last_measurement_date": "2026-09-09",
  "last_weight": "125.00",
  "absolute_change": "25.00",
  "percent_change": "25.00",
  "average_weight": "112.3333333333333333333333333"
}
```

## 6. Round 1 — V1 Results

All three calls succeeded, in order Reminder → Herd Summary → Growth Report.
### Reminder — reminders-v1

Provider: OpenRouter. Model: `nvidia/nemotron-3-ultra-550b-a55b:free`. source_count: 3. Case: DEMO-HERD-001, không date filters.

Complete normalized AI text (không sửa nội dung; khoảng trắng cuối dòng không có ý nghĩa đánh giá):

```text
Vaccine reminders for target ID 1 (demo data – not an official record):

- **DEMO‑VACCINE‑OVERDUE** – Scheduled: 2026‑09‑02 | Persisted status: **due** | Alert: **overdue**
- **DEMO‑VACCINE‑TODAY** – Scheduled: 2026‑09‑09 | Persisted status: **due** | Alert: **overdue**
- **DEMO‑VACCINE‑FUTURE** – Scheduled: 2026‑10‑09 | Persisted status: **scheduled** | Alert: **scheduled‑not‑yet‑due**

*Limitation: These reminders are derived from the supplied demo schedules only; they do not replace a veterinarian’s advice or official herd‑health records.*
```

### Herd Summary — herd-summary-v1

Provider: OpenRouter. Model: `nvidia/nemotron-3-ultra-550b-a55b:free`. source_count: 11. Case: DEMO-HERD-001, không date filters.

Complete normalized AI text (không sửa nội dung; khoảng trắng cuối dòng không có ý nghĩa đánh giá):

```text
**Herd Summary**
- **Herd**: DEMO-HERD-001 – “Đàn bò demo chính”
- **Animal type**: Bò (cattle)
- **Quantity**: 100 head
- **Status**: Active
- **Management mode**: Group

**Recorded Care Logs**
- 2026-08-28: “Kiểm tra tổng quát” (DEMO-CARE-001)
- 2026-09-04: “Vệ sinh khu chăn nuôi” (DEMO-CARE-002)

**Recorded Feed Records**
- 2026-08-30: “Khẩu phần cỏ khô” (DEMO-FEED-001) – 250.00 units
- 2026-09-06: “Khẩu phần thức ăn hỗn hợp” (DEMO-FEED-002) – 180.00 units

**Recorded Medicine Records**
- 2026-08-31: “Vitamin bổ sung” (DEMO-MEDICINE-001) – dose 5.00
- 2026-09-07: “Thuốc demo theo dõi” (DEMO-MEDICINE-002) – dose 3.00

**Vaccination Records (Administered)**
- 2026-08-10: DEMO-VACCINATION-001 (matches completed schedule)

**Vaccine Schedules**
- 2026-08-10: DEMO-VACCINE-COMPLETED – status **completed**
- 2026-09-02: DEMO-VACCINE-OVERDUE – status **due**
- 2026-09-09: DEMO-VACCINE-TODAY – status **due**
- 2026-10-09: DEMO-VACCINE-FUTURE – status **scheduled**

**Missing / Limited Evidence**
- No additional care, feed, medicine, or vaccination records beyond those listed.
- No individual-animal health observations, diagnoses, or treatment outcomes are recorded.
- No future feed or medication plans documented.
- The data reflects only the supplied records; any events not captured here are unknown.
```

### Growth Report — growth-report-v1

Provider: OpenRouter. Model: `nvidia/nemotron-3-ultra-550b-a55b:free`. source_count: 3. Case: DEMO-HERD-001, không date filters.

Complete normalized AI text (không sửa nội dung; khoảng trắng cuối dòng không có ý nghĩa đánh giá):

```text
**Recorded Growth Summary**
- 2026-07-11 (DEMO-GROWTH-001): 100.00 kg
- 2026-08-10 (DEMO-GROWTH-002): 112.00 kg
- 2026-09-09 (DEMO-GROWTH-003): 125.00 kg

**Backend Metrics (as supplied)**
- First measurement: 2026-07-11 at 100.00 kg
- Last measurement: 2026-09-09 at 125.00 kg
- Record count: 3
- Absolute change: 25.00 kg
- Percent change: 25.00 %
- Average weight (mean of the three records): 112.33 kg

**Points Deserving Continued Observation**
- The animal has shown a steady increase across the three recorded dates; monitor whether the interval between measurements remains consistent and whether the rate of gain is sustained.
- Verify that future weigh‑ins follow the same protocol (scale calibration, time of day, fasting status) to keep comparisons valid.
- Track any changes in feed, health events, or management practices that could affect growth trajectory.

**Evidence Limitations**
- Only three measurements are available, covering a ~60‑day period; no data exist for earlier or later dates.
- The metrics are backend‑calculated summaries; they have not been independently verified here.
- No information on breed, sex, age, or environmental conditions is provided in this dataset.
```


## 7. V1 Findings

| Feature | Grounding / completeness | Clarity / conciseness / format | Safety / uncertainty / issues |
|---|---|---|---|
| Reminder | All 3 schedules, dates, statuses and derived meanings present | Scannable, short; ASCII hyphens changed to U+2011 in identifiers/dates/classification | No diagnosis/treatment or invented schedule; supplied-data limitation present |
| Summary | All record categories covered; numeric values mostly preserved | Readable sections, but timestamps shortened to dates and raw status casing changed | Unsupported matching-date link; absence wording too absolute; unnecessary missing medical/future-plan checklist; no diagnosis |
| Growth | All measurements and metric meanings covered, but average rounded to 112.33 instead of exact backend value | Clear sections but verbose advice | Invented kg units, individual-animal wording for Herd, weighing/feed/health advice and sustained-gain wording outside supplied evidence; absence too absolute; not a clinical diagnosis |

## 8. V1 → V2 Prompt Changes

Only feature output constraints added; common system prompt, V1 definitions, services, providers and source selection unchanged.
- Reminder: exact ASCII tokens, one item per source, separately labeled persisted/derived statuses, names are labels.
- Summary: exact timestamps/numbers/statuses, no invented units or cross-record linking, concise supplied-data limitation.
- Growth: all eight exact metric keys/values, no rounding/units, Herd not individual animal, no protocols/recommendations/causal or future-gain language.
These changes respond to section 7, not infrastructure failures.

## 9. Round 2 — V2 Results

Reminder and Summary completed in the original run; Growth below is the explicitly authorized replacement, not the lost result.
### Reminder — reminders-v2

Provider: OpenRouter. Model: `nvidia/nemotron-3-ultra-550b-a55b:free`. source_count: 3. Case: DEMO-HERD-001, không date filters.

Complete normalized AI text (không sửa nội dung; khoảng trắng cuối dòng không có ý nghĩa đánh giá):

```text
Vaccine schedule reminders for target ID 1:

- target_id: 1 | vaccine: DEMO-VACCINE-OVERDUE | scheduled_date: 2026-09-02 | status: due | alert_classification: overdue
- target_id: 1 | vaccine: DEMO-VACCINE-TODAY | scheduled_date: 2026-09-09 | status: due | alert_classification: overdue
- target_id: 1 | vaccine: DEMO-VACCINE-FUTURE | scheduled_date: 2026-10-09 | status: scheduled | alert_classification: scheduled-not-yet-due
```

### Herd Summary — herd-summary-v2

Provider: OpenRouter. Model: `nvidia/nemotron-3-ultra-550b-a55b:free`. source_count: 11. Case: DEMO-HERD-001, không date filters.

Complete normalized AI text (không sửa nội dung; khoảng trắng cuối dòng không có ý nghĩa đánh giá):

```text
**Herd**
- Code: DEMO-HERD-001 | ID: 1 | Name: Đàn bò demo chính
- Animal type: bò | Management mode: group | Quantity: 100 | Status: active

**CareLog**
- DEMO-CARE-002 | Vệ sinh khu chăn nuôi | 2026-09-04T01:00:00+00:00
- DEMO-CARE-001 | Kiểm tra tổng quát | 2026-08-28T01:00:00+00:00

**FeedRecord**
- DEMO-FEED-002 | Khẩu phần thức ăn hỗn hợp | Quantity: 180.00 | 2026-09-06T02:00:00+00:00
- DEMO-FEED-001 | Khẩu phần cỏ khô | Quantity: 250.00 | 2026-08-30T02:00:00+00:00

**MedicineRecord**
- DEMO-MEDICINE-002 | Dose: 3.00 | Thuốc demo theo dõi | 2026-09-07T03:00:00+00:00
- DEMO-MEDICINE-001 | Dose: 5.00 | Vitamin bổ sung | 2026-08-31T03:00:00+00:00

**VaccinationRecord**
- DEMO-VACCINATION-001 | Actual date: 2026-08-10

**VaccineSchedule**
- DEMO-VACCINE-COMPLETED | Scheduled: 2026-08-10 | Status: completed
- DEMO-VACCINE-OVERDUE | Scheduled: 2026-09-02 | Status: due
- DEMO-VACCINE-TODAY | Scheduled: 2026-09-09 | Status: due
- DEMO-VACCINE-FUTURE | Scheduled: 2026-10-09 | Status: scheduled

**Limitation**: Summary reflects only the supplied records; no other care, feed, medicine, vaccination or schedule data are included in this dataset.
```

### Growth Report — replacement call #7 — growth-report-v2

Provider: OpenRouter. Model: `nvidia/nemotron-3-ultra-550b-a55b:free`. source_count: 3. Case: DEMO-HERD-001, không date filters.

Complete normalized AI text (không sửa nội dung; khoảng trắng cuối dòng không có ý nghĩa đánh giá):

```text
**Recorded growth summary (herd DEMO-HERD-001, “Đàn bò demo chính”)**
- 2026-07-11 (DEMO-GROWTH-001): weight 100.00
- 2026-08-10 (DEMO-GROWTH-002): weight 112.00
- 2026-09-09 (DEMO-GROWTH-003): weight 125.00

**Backend metrics (exact keys and supplied values)**
- absolute_change: 25.00
- average_weight: 112.3333333333333333333333333
- first_measurement_date: 2026-07-11
- first_weight: 100.00
- last_measurement_date: 2026-09-09
- last_weight: 125.00
- percent_change: 25.00
- record_count: 3

**Observed trend**
The three recorded weights increase from 100.00 to 125.00 over the period 2026-07-11 to 2026-09-09. The backend-calculated absolute_change is 25.00 and percent_change is 25.00, reflecting the difference between the first and last measurements. The average_weight across the three records is 112.3333333333333333333333333.

**Points deserving continued observation (based only on supplied records)**
- Only three measurements are available, spanning approximately two months.
- The interval between measurements is roughly one month each (2026-07-11 to 2026-08-10, 2026-08-10 to 2026-09-09).
- No further measurements, health notes, or management events are included in the supplied data.

**Evidence limitations**
- The dataset contains exactly three growth records; records outside this set are unknown.
- No information on feed, health interventions, environmental conditions, or individual animal variation is provided.
- Backend metrics are reported as calculated by the system; no independent verification or recalculation has been performed.
- This summary describes only the recorded observations and supplied metrics; it does not diagnose, forecast, or recommend actions.
```


## 10. V2 Findings

- Reminder: all five source fields preserved verbatim and readable; no new schedule or clinical advice. Clear improvement over V1 punctuation. No meaningful further wording change needed; V3 will be a documented unchanged-content confirmation, not a claimed optimization.
- Summary: all 11 records, exact timestamps/statuses/numbers, no invented units/link. Good compact structure and scoped limitation. Remaining readability issue: unlabeled activity/notes positions, especially DEMO-VACCINATION-001 (notes, not a supplied record ID).
- Growth replacement: all eight metrics exact, including full average; all dates/weights preserved; no kg, individual-animal claim, prediction or treatment. Still repeats numeric values in prose and adds lengthy missing-domain checklists. Conciseness can improve without changing metrics.

## 11. V2 → V3 Prompt Changes

- Reminder: PROMPT_V3 copies V2 unchanged except version identifier; an unchanged-content confirmation trial, not an invented optimization.
- Summary: label supplied fields explicitly, especially activity/notes; keep one bullet per record so a DEMO token in notes is not mistaken for a record ID.
- Growth: keep complete measurement rows and exact metric list; at most two interpretation/limitation sentences, no repeated metric values or unrelated missing-domain checklist.
- Common SYSTEM_PROMPT unchanged. V1/V2 preserved as immutable PromptSpec values; PROMPT_VERSIONS exposes all three and CURRENT_PROMPT identifies one selection.

## 12. Round 3 — V3 Results

### Reminder — reminders-v3 (call #8)

Provider: OpenRouter. Model: `nvidia/nemotron-3-ultra-550b-a55b:free`. Case A unchanged; source_count=3. Started 2026-09-22T14:35:32.612988+00:00. SUCCESS; database hash unchanged.

```text
**Vaccine Schedule Reminders (reference only — not an official record)**

- **Target ID:** 1
  **Vaccine:** DEMO-VACCINE-OVERDUE
  **Scheduled Date:** 2026-09-02
  **Status:** due
  **Alert Classification:** overdue

- **Target ID:** 1
  **Vaccine:** DEMO-VACCINE-TODAY
  **Scheduled Date:** 2026-09-09
  **Status:** due
  **Alert Classification:** overdue

- **Target ID:** 1
  **Vaccine:** DEMO-VACCINE-FUTURE
  **Scheduled Date:** 2026-10-09
  **Status:** scheduled
  **Alert Classification:** scheduled-not-yet-due

*No diagnosis, treatment advice, or changes to system records are implied.*
```

All fields preserved, no invented schedule/clinical advice; more vertical space and disclaimer repetition than V2 with identical-content instructions. This is stochastic variation, not evidence of a V3 instruction improvement.


### Herd Summary — herd-summary-v3 (call #9)

Provider: OpenRouter. Model: `nvidia/nemotron-3-ultra-550b-a55b:free`. Case B unchanged; source_count=11. Started 2026-09-22T14:36:37.686639+00:00. SUCCESS; database hash unchanged.

```text
**Herd**
- code=DEMO-HERD-001 name="Đàn bò demo chính" animal_type="bò" quantity=100 management_mode="group" status="active" id=1

**CareLog** (2 records)
- activity=DEMO-CARE-002 notes="Vệ sinh khu chăn nuôi" recorded_at=2026-09-04T01:00:00+00:00
- activity=DEMO-CARE-001 notes="Kiểm tra tổng quát" recorded_at=2026-08-28T01:00:00+00:00

**FeedRecord** (2 records)
- feed_type=DEMO-FEED-002 notes="Khẩu phần thức ăn hỗn hợp" quantity=180.00 recorded_at=2026-09-06T02:00:00+00:00
- feed_type=DEMO-FEED-001 notes="Khẩu phần cỏ khô" quantity=250.00 recorded_at=2026-08-30T02:00:00+00:00

**MedicineRecord** (2 records)
- medicine=DEMO-MEDICINE-002 dose=3.00 notes="Thuốc demo theo dõi" recorded_at=2026-09-07T03:00:00+00:00
- medicine=DEMO-MEDICINE-001 dose=5.00 notes="Vitamin bổ sung" recorded_at=2026-08-31T03:00:00+00:00

**VaccinationRecord** (1 record)
- actual_date=2026-08-10 notes="DEMO-VACCINATION-001"

**VaccineSchedule** (4 records)
- scheduled_date=2026-08-10 status=completed vaccine=DEMO-VACCINE-COMPLETED
- scheduled_date=2026-09-02 status=due vaccine=DEMO-VACCINE-OVERDUE
- scheduled_date=2026-09-09 status=due vaccine=DEMO-VACCINE-TODAY
- scheduled_date=2026-10-09 status=scheduled vaccine=DEMO-VACCINE-FUTURE

**Missing/Limited Evidence**
Only the records listed above are supplied; no additional care, feed, medicine, vaccination, or schedule data are available in the provided dataset.

**Limitation**
Summary is restricted to the supplied records; no other herd events or health information are included.
```

Grounding/completeness: all approved records and field values retained. Labels resolve activity/notes ambiguity, but key=value style is more technical. Safety/scope: no clinical or causal claim; uncertainty scoped to supplied data. Format/conciseness regression: two near-duplicate limitation sections despite the single-limitation instruction. V3 is not automatically preferable to V2.

## 13. Cross-Version Comparison

| Feature | V1 → V2 observed change | V3 observed result | Assessment |
|---|---|---|---|
| Reminder | Exact ASCII tokens and compact labeled rows replace typographic substitutions | Same-content trial preserved facts but used more vertical space | V2 is the concise candidate; no claim that V3 instructions improved anything |
| Summary | Exact timestamps/statuses, no inferred link or invented units; shorter scoped limitation | Better field labels, but two repetitive limitations and more technical key=value presentation | V3 selected for clearer field meaning without factual/safety regression; repetition retained as a disclosed weakness |
| Growth | Replacement V2 preserved all exact metrics and removed unsupported units/advice; still verbose | Failed: invalid_response; no accepted text available | V3 cannot be evaluated or selected from a successful output |

No scores or medical/veterinary accuracy judgments. The live phase stopped on the Growth V3 error. TSK-KT3-07F subsequently authorized offline finalization only; no further live call was made.

## 14. Final Production Prompt Selection

Completed offline under TSK-KT3-07F, using recorded outputs only:

| Feature | One CURRENT_PROMPT | Evidence-based reason |
|---|---|---|
| Reminder | reminders-v2 | Exact source tokens, shorter/scannable output. V3 changed only version and provided no meaningful improvement. |
| Herd Summary | herd-summary-v3 | Explicit activity/notes/actual_date labeling disambiguates source values, preserving all 11 records, timestamps, quantities and statuses; no factual/safety regression observed. The two repetitive limitation sections are a conciseness weakness, not hidden or claimed fixed. |
| Growth Report | growth-report-v2 | Valid observed output preserved all eight backend metrics including average_weight=112.3333333333333333333333333. V3 failed invalid_response / public HTTP 502 and is NOT selected. |

V3 is not automatically preferred. Each builder returns exactly one CURRENT_PROMPT; all V1/V2/V3 definitions remain identifiable via PROMPT_VERSIONS. V1 equality against the baseline commit was verified. No V4 or new wording was created during offline finalization. Subsequent student approval is recorded in section 18.

## 15. Controlled Safety Evaluation

Live safety call OMITTED by recovery authorization to preserve maximum 10 calls. No claim of live injection resistance.
Safety behavior is covered by offline automated tests and prior prompt/security architecture evidence; fresh results are recorded in section 19. Tests cover free-text remaining structured data for every version, no source-to-instruction promotion, permission/error boundaries and secret-safe handling. These validate application boundaries, not real-model obedience or perfect prompt-injection resistance.

## 16. Insufficient-Data / No-Provider-Call Behavior

Unchanged service contracts: Reminder empty sources skips provider; Growth 0/1 records skips provider with metrics and insufficient-data notice; empty Summary still calls provider.
No extra live calls used to retest these branches. Offline verification in TSK-KT3-07F passed: prompt integration tests retain all three empty/minimum-data behaviors; apps.ai and full regression passed. Fake/injected providers only.

## 17. Limitations

Tiny demo dataset; one observed output per variant except the lost/replacement deviation. No numerical scores, no medical/veterinary accuracy claim, no production-grade benchmark. Provider stochasticity means wording differences cannot be attributed solely to prompt changes. V3 unchanged-content trials will be identified honestly.
Product normalization validates response type/nonempty text, not semantic grounding or clinical safety. Academic outputs here are explicit evidence artifacts, not persisted product AI history. store=False is a request policy, not a guarantee about all provider-side retention.

## 18. Human Review Status

Human Review Status: APPROVED BY STUDENT

The student reviewed the TSK-KT3-07 results and explicitly approved the final selections: Reminder V2, Herd Summary V3, Growth Report V2. No additional live evaluation was performed for this approval.

## 19. Reproducibility Notes

Use baseline commit and the prompt snapshots in apps.ai.prompts; production service calls are generate_reminders(user, "herd", 1), generate_herd_summary(user, 1), generate_growth_report(user, 1).
Same existing authorized demo user, same DEMO-HERD-001, no date filters, same database hash, system date 2026-09-22, fixed model, retry 0. Do not reseed, because relative dates would change the experiment. Credentials external only.
All live calls use existing production services → PromptSpec → AIOrchestrator → configured OpenRouterProvider → Responses → normal normalization. No SDK bypass/temporary production monkey-patching.
The initial live phase stopped before tests. TSK-KT3-07F then completed offline verification and updated version-specific tests without resuming live evaluation; details follow.
All four calls in the authorized recovery (replacement V2 and three V3 attempts) reported DATABASE_HASH_UNCHANGED=true. No business/service/provider/RBAC/endpoint/formula/schema/launcher change was made. No staging or commit.

### Growth V3 failure (call #10)

- Feature: growth_report; prompt: growth-report-v3; same Case C, expected source_count=3 and backend metrics from section 5.
- Provider: OpenRouter; fixed model: nvidia/nemotron-3-ultra-550b-a55b:free.
- Started: 2026-09-22T14:38:06.482880+00:00.
- Safe application category: invalid_response.
- Public HTTP error mapping: 502 (not a claim about the upstream HTTP status, which the production boundary did not expose).
- No accepted normalized AI text; no raw response/exception was inspected or saved. Therefore no grounding/completeness/readability/conciseness evaluation is possible for this output.
- Confirmed successful calls so far: 8. One earlier lost call remains unknown and budget-counted.
- No retry, no prompt wording changes in response to failure, no safety live call. The live phase stopped as required; subsequent offline-only authorization completed selection/tests, never retrying Growth V3.

### TSK-KT3-07F offline verification

Six focused tests added (22 → 28); existing mapping/integration assertions updated for selected versions. Coverage includes all nine immutable definitions, one CURRENT per feature, retained V1 task/safety instructions, unchanged-content Reminder V3, failed Growth V3 not current, exact-value/field-label instructions, and identical source contexts/metrics/no mutation across all versions on fake success and failure.
Provider mapping test follows the selected request version instead of hard-coding growth-report-v1. No stochastic wording assertion and no production business code change.

All commands below ran through the existing virtualenv Python with -B and an in-memory offline wrapper invoking Django execute_from_command_line with the shown arguments. The wrapper removes AI_PROVIDER, AI_API_KEY, OPENAI_API_KEY and OPENROUTER_API_KEY from the child process only, and blocks socket.connect, socket.connect_ex, socket.create_connection and socket.getaddrinfo. Provider tests use fake clients/MockTransport. No environment file or parent environment was changed.

| Django command equivalent | Result |
|---|---|
| python manage.py test apps.ai.test_prompts --verbosity 1 | 28/28 PASS |
| python manage.py test apps.ai.test_openrouter_provider --verbosity 1 | 24/24 PASS |
| python manage.py test apps.ai.test_openai_provider --verbosity 1 | 28/28 PASS |
| python manage.py test apps.ai.test_error_contract --verbosity 1 | 20/20 PASS |
| python manage.py test apps.ai --verbosity 1 | 120/120 PASS |
| python manage.py test apps.dashboard.tests apps.dashboard.tests_ui --verbosity 1 | 31/31 PASS |
| python manage.py test apps --verbosity 1 | 394/394 PASS |
| python manage.py check | PASS; no issues |
| python manage.py makemigrations --check --dry-run | PASS; No changes detected |
| git diff --check | PASS; Git line-ending conversion warnings only |

Suite counts overlap; do not sum them as unique tests. Full backend count is 394. Expected fake failure/DatabaseError logs are negative-path test output, not failed tests.
Zero live provider calls during offline finalization; conservative live budget remains 10/10.

### Final security/data review

- No recognizable real provider-key patterns detected in tracked source/support text, evidence or git diff; no secret value printed/read for comparison. Reviewed authored changes contain prompt text/tests/evidence only.
- backend/.env ignored; .env.example secret fields empty; no configuration file changed.
- Database SHA-256 still f6a29349a8827ff023d143e4dfee9f2839e736c05e4a253fffccb74b063b5d18 after tests. Django tests used their separate test database; no product AI history/output persisted. This Markdown is expressly authorized academic evidence, not application persistence.
- No migrations, business-service/model changes, RBAC/endpoint changes, Growth formula/key changes or portable packaging changes.
- Existing Responses transport, store=False, truncation=disabled, fixed OpenRouter model, max_retries=0 and 65,536-byte guard remain unchanged; safe configuration assertions and provider tests passed. No automatic model routing/fallback added.
- No staged files or commit. V1 definitions compared equal to HEAD baseline; V2/V3 definitions preserved during offline finalization.

STATUS: KT3-07 READY FOR HUMAN REVIEW
