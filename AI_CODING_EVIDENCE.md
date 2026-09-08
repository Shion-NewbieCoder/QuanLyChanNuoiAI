# Minh chứng sử dụng AI khi lập trình

## 1. Phạm vi và tính trung thực của bằng chứng

AI/Codex được sử dụng như trợ lý lập trình cho project. Output của AI
không được xem là source of truth và không được chấp nhận tự động.
Assignment, Requirements, Design, Implementation Plan và source hiện tại luôn
có ưu tiên cao hơn gợi ý của AI.

Tài liệu này là bản tổng hợp các workflow thực tế tiêu biểu được cung
cấp trong quá trình review cuối, kết hợp với code, test và Git evidence
hiện có. Đây không phải transcript đầy đủ hoặc archive hội thoại có
timestamp. Tài liệu không suy diễn model name, ngày giờ, code ownership hay
sự kiện không có trong bằng chứng được cung cấp.

Quy tắc chấp nhận chung:

- Prompt được giới hạn theo một task và source-of-truth cụ thể.
- AI phải dừng và báo `BLOCKED` khi thiếu business/design decision quan trọng.
- Business rule mơ hồ không được AI tự chọn.
- Human-approved Project Design Decision được dùng khi source chưa đủ.
- Implementation chỉ được chấp nhận sau focused tests, regression, system
  checks và migration-drift checks phù hợp.

## 2. Evidence Record 1 — TSK-023 AI Growth Report

### A. Prompt sent to coding AI

Mục tiêu prompt là triển khai TSK-023, nhưng trước hết phải kiểm tra
contract và dừng nếu request/date/empty-data/output semantics chưa được xác
định. Trích đoạn chỉ dẫn thực tế:

> Before modifying files, inspect exact source sections for:
> - TSK-023
> - AI Growth Report
> ...
> If any material part is ambiguous:
> STOP and report BLOCKED.
> Do NOT invent API behavior.

### B. AI/Codex response

AI trả về `TSK_023_IMPLEMENTATION_STATUS: BLOCKED` và không sửa file. Response
xác định endpoint duy nhất đã có là `POST /api/ai/growth-report`, nhưng
các nội dung sau chưa đủ để implement an toàn:

- field nhận diện Herd;
- semantics của date range;
- allowlist dữ liệu Herd/GrowthRecord gửi cho AI;
- deterministic metrics;
- xử lý khi có 0 hoặc 1 record;
- exact response schema;
- persistence semantics.

### C. Code/files assisted

Sau clarification, implementation hiện tại nằm tại:

- `backend/apps/ai/growth_report.py`
- `backend/apps/ai/serializers.py`
- `backend/apps/ai/views.py`
- `backend/apps/ai/urls.py`
- `backend/apps/ai/tests.py`

Feature sử dụng boundary có sẵn trong `backend/apps/ai/orchestrator.py`. Các path
trên đã được kiểm tra là tồn tại; mapping này chỉ ghi
"AI-assisted implementation/review", không tuyên bố AI viết 100% file.

### D. Student review / verification

Sinh viên/người kiểm duyệt chấp nhận kết luận `BLOCKED` thay vì yêu cầu
AI đoán contract. Project Design Decision `PD-AI-GROWTH-001` sau đó được
phê duyệt và hiện được ghi trong:

- `01_requirements_chan_nuoi_ai.md`
- `02_design_chan_nuoi_ai.md`
- `03_implementation_plan_chan_nuoi_ai_reviewed.md`

### E. Corrections made after review

Clarification chốt:

- `POST /api/ai/growth-report` với `herd_id` bắt buộc;
- `start_date`/`end_date` tùy chọn, độc lập và filter inclusive trên
  `GrowthRecord.measurement_date`;
- Herd allowlist `id`, `code`, `name`;
- GrowthRecord allowlist `measurement_date`, `weight`, `notes`;
- deterministic application metrics;
- tối thiểu 2 record mới gọi AI; 0/1 record trả HTTP 200 và không gọi
  provider;
- output transient và access theo `PD-ROLE-001`.

Documentation backtrack trả `GROWTH_REPORT_BACKTRACK_STATUS: PASS` và
`TSK_023_UNBLOCKED: YES` trước khi implementation tiếp tục.

### F. Test or regression evidence

Kết quả verification được ghi nhận trong workflow:

- `TSK_023_IMPLEMENTATION_STATUS: PASS`
- focused Growth Report tests: 15/15 PASS
- full regression tại thời điểm đó: 229/229 PASS
- Django check: PASS
- migration drift: NONE

Evidence này cho thấy AI không được phép lấp chỗ trống requirement; human
review cung cấp contract trước khi code và tests được chấp nhận.

## 3. Evidence Record 2 — TSK-024 Shared AI Output Safety

### A. Prompt sent to coding AI

Prompt yêu cầu chỉ implement output validation/safety đã được ghi trong source,
đồng thời không tự thêm size limit, Markdown/HTML policy, keyword blacklist,
external moderation service hay persistence. Chỉ dẫn quan trọng:

> If the source does not define a material safety rule,
> do NOT invent one.

### B. AI/Codex response

Kết quả được ghi nhận:

- `TSK_024_IMPLEMENTATION_STATUS: PASS`
- contract chỉ yêu cầu `AIResponse.text` không rỗng và provider marker hợp lệ;
- validation dùng chung qua `AIOrchestrator`;
- leading/trailing whitespace được loại bỏ;
- sai type, empty hoặc whitespace-only output bị từ chối;
- malformed provider output trả safe HTTP 500 `internal_error`, không lộ raw output
  hay provider details;
- không thêm các moderation rule không có trong source.

### C. Code/files assisted

Các file được báo cáo trong workflow và đã được xác minh hiện còn
tồn tại:

- `backend/apps/ai/safety.py`
- `backend/apps/ai/orchestrator.py`
- `backend/apps/ai/reminders.py`
- `backend/apps/ai/herd_summary.py`
- `backend/apps/ai/growth_report.py`
- `backend/apps/ai/tests.py`

### D. Student review / verification

Implementation được chấp nhận vì shared safety boundary phù hợp source,
không thêm undocumented moderation semantics và giữ nguyên source-of-truth
protections.

### E. Corrections made after review

Output validation được tập trung tại `validate_and_normalize_output()` và được
gọi bởi `AIOrchestrator.run()`, thay vì để từng feature chấp nhận raw provider
output. Feature notices được kết hợp với shared safety notice.

### F. Test or regression evidence

- focused output-safety tests: 20/20 PASS
- full regression tại thời điểm đó: 234/234 PASS
- migration drift: NONE

## 4. Evidence Record 3 — TSK-030 Git requirement

### A. Prompt sent to coding AI

Final-delivery audit yêu cầu kiểm tra Git repository và lịch sử commit thay vì
chỉ dựa vào nội dung source.

### B. AI/Codex response

Kết quả audit ban đầu là:

```text
TSK_030_IMPLEMENTATION_STATUS: BLOCKED
GIT_REPOSITORY_STATUS: NOT A GIT REPOSITORY
GIT_REQUIREMENT_STATUS: BLOCKED
```

Lý do: assignment yêu cầu commit rõ ràng nhưng `.git` chưa tồn tại.

### C. Code/files assisted

Không có business code được gán cho record này. Corrective action liên quan
repository initialization, staging các current snapshot và delivery documentation.

### D. Student review / verification

Sinh viên/người kiểm duyệt không đổi artificially kết quả thành PASS. Chỉ
dẫn corrective yêu cầu repository thật, không backdate, không tạo fake history,
không bịa author hoặc hash.

### E. Corrections made after review

Repository được khởi tạo trong bước Final Delivery và các truthful current
snapshots được commit. Không tuyên bố đây là lịch sử phát triển cũ.

### F. Test or regression evidence

Git evidence đã được kiểm tra lại trước khi tạo tài liệu này. Ba
commit Final Delivery thực sự có trong history:

```text
8d2df9a docs: finalize demo data and project delivery
a81d995 feat: add React application interface scaffold
9a74b3b feat: add livestock management backend
```

Trước corrective documentation này, `git status --short` sạch. Current history còn
có commit Criterion 04 được xác minh ở Evidence Record 4.

## 5. Evidence Record 4 — BTKN2 Criterion 04 Search/Filter/Sort

### A. Prompt sent to coding AI

Sau khi TSK-001..TSK-030 đã PASS, final BTKN2 audit vẫn được yêu cầu
kiểm tra trực tiếp theo assignment. Corrective prompt sau đó chỉ cho phép:

- DRF `SearchFilter`;
- exact validated filtering;
- DRF `OrderingFilter`;
- resource-specific field allowlists;
- giữ nguyên RBAC;
- không schema change hay Statistics/AI redesign.

### B. AI/Codex response

Final audit ban đầu trả:

```text
CRITERION_04_SEARCH_FILTER_SORT: FAIL
```

Lý do là search và client-selectable ordering không tồn tại trên business
CRUD APIs; filtering khi đó chỉ có trong report/AI flows chuyên biệt.

Sau corrective pass, AI/Codex trả:

```text
BTKN2_CRITERION_04_STATUS: PASS
SEARCH_IMPLEMENTATION: DRF SearchFilter with ?search=<text>
FILTER_IMPLEMENTATION: Reusable ExactFieldFilterBackend
ORDERING_IMPLEMENTATION: DRF OrderingFilter with ?ordering=<field> / -<field>
```

### C. Code/files assisted

- `backend/config/filters.py`
- `backend/apps/test_query_capabilities.py`
- `backend/apps/herds/views.py`
- `backend/apps/pens/views.py`
- `backend/apps/care/views.py`
- `backend/apps/vaccinations/views.py`
- `backend/apps/growth/views.py`
- `backend/apps/reproduction/views.py`
- `backend/apps/sales/views.py`

### D. Student review / verification

Sinh viên/người kiểm duyệt không dùng trạng thái 30/30 TSK để bỏ qua
tiêu chí gốc. Corrective prompt được giới hạn theo đúng gap, exact model
fields và existing role policy.

### E. Corrections made after review

Search, exact filtering và restricted ordering được thêm cho Herd, Animal,
AnimalGroup, Pen, CareLog, FeedRecord, MedicineRecord, VaccineSchedule,
VaccinationRecord, GrowthRecord, ReproductionRecord và SaleRecord. Không thêm model,
migration hay dependency.

### F. Test or regression evidence

- focused query tests: 17/17 PASS
- full regression: 266/266 PASS
- Django check: PASS
- migration drift: NONE
- verified commit: `9f9a4bd feat: add search filtering and ordering to business APIs`

## 6. Evidence Record 5 — TSK-027 deterministic demo data

### A. Prompt sent to coding AI

Prompt TSK-027 yêu cầu kiểm tra seed contract và không tự bịa demo users,
passwords, counts, enum hay schema.

### B. AI/Codex response

Response ban đầu là `TSK_027_IMPLEMENTATION_STATUS: BLOCKED`,
`FILES_MODIFIED: NONE`, với các thiếu sót:

- deterministic demo dataset chưa được xác định;
- demo-account và credential policy chưa được xác định;
- stable identifiers chưa được xác định;
- vaccine date anchoring chưa được xác định;
- expected post-seed counts chưa được xác định.

### C. Code/files assisted

- `backend/apps/dashboard/management/commands/seed_demo.py`
- `backend/apps/dashboard/tests_seed_demo.py`

### D. Student review / verification

AI không được chọn arbitrary user/password/count. Human review phê duyệt
`PD-SEED-001`, hiện có trong Requirements, Design và Implementation Plan.

### E. Corrections made after review

`PD-SEED-001` xác định duy nhất command `python manage.py seed_demo`, DEBUG-only
guard, ba local demo users/roles, local public-demo credential policy, reserved `DEMO-*`
identifiers, exact counts, `anchor_date = timezone.localdate()`, relative vaccine
scenarios, growth/statistics/AI factual source coverage, idempotence và non-demo
preservation. Backtrack kết thúc với `SEED_BACKTRACK_STATUS: PASS` và
`TSK_027_UNBLOCKED: YES`.

### F. Test or regression evidence

- `TSK_027_IMPLEMENTATION_STATUS: PASS`
- seed execution: PASS
- repeated seed/idempotence: PASS
- focused seed tests: 6/6 PASS
- full regression tại thời điểm đó: 249/249 PASS
- migration drift: NONE

## 7. Mapping AI assistance to project code

| Evidence | Task | Files/modules affected | AI assistance | Student verification |
|---|---|---|---|---|
| Growth Report contract/implementation | TSK-023 | `backend/apps/ai/growth_report.py`, `serializers.py`, `views.py`, `urls.py`, `tests.py`; uses `orchestrator.py` | AI-assisted contract audit, implementation and review | Human-approved `PD-AI-GROWTH-001`; 15 focused tests, 229 regression tests, check and drift verification |
| Shared output safety | TSK-024 | `backend/apps/ai/safety.py`, `orchestrator.py`, `reminders.py`, `herd_summary.py`, `growth_report.py`, `tests.py` | AI-assisted implementation/review of shared validation boundary | Verified no invented moderation semantics; 20 focused tests and 234 regression tests |
| Deterministic demo data | TSK-027 | `backend/apps/dashboard/management/commands/seed_demo.py`, `backend/apps/dashboard/tests_seed_demo.py` | AI-assisted design-gap detection, implementation and review | Human-approved `PD-SEED-001`; 6 focused tests, repeat execution and 249 regression tests |
| Search/filter/order correction | BTKN2 Criterion 04 | `backend/config/filters.py`, `backend/apps/test_query_capabilities.py`, seven business `views.py` modules | AI-assisted final audit, scoped correction and verification | 17 focused tests, 266 regression tests, check/drift verification, commit `9f9a4bd` |

Không có row nào trong bảng tuyên bố AI tự chủ hoặc viết 100% file.

## 8. Student verification / correction summary

Workflow lặp lại được sử dụng:

1. Đọc assignment, Requirements, Design, Plan và current source.
2. Gửi prompt có phạm vi cụ thể cho coding AI.
3. Yêu cầu `STOP`/`BLOCKED` nếu requirement quan trọng mơ hồ.
4. Sinh viên/người kiểm duyệt xem lại response và evidence.
5. Xin/phê duyệt human Project Design Decision khi source chưa đủ.
6. Re-prompt với contract đã làm rõ và scope bị giới hạn.
7. Chạy focused tests cho thay đổi.
8. Chạy full regression.
9. Chạy Django system check và migration-drift check.
10. Chỉ chấp nhận khi evidence PASS.

Ví dụ cụ thể:

- TSK-023 bị chặn trước khi Growth Report contract được làm rõ.
- TSK-027 bị chặn trước khi deterministic seed contract được phê duyệt.
- TSK-030 bị chặn thay vì tạo Git history giả.
- BTKN2 Criterion 04 được phát hiện thiếu sau 30/30 TSK và sau đó
  được sửa, test và commit riêng.

## 9. AI limitations và trách nhiệm con người

- AI suggestion không phải source of truth.
- Assignment, approved documents và current code có thứ tự ưu tiên cao hơn.
- AI không được tự phát minh business rule còn thiếu.
- Human-approved Project Design Decisions giải quyết ambiguity.
- Tests, checks và Git evidence được dùng để xác minh thay đổi.
- Git history được giữ trung thực, không backdate hoặc mô tả snapshot như
  lịch sử phát triển cũ.
- Tài liệu này ghi các ví dụ đại diện, không tuyên bố là toàn bộ
  hội thoại với AI.

## 10. Privacy và delivery safety

Artifact không chứa AI API key, Django secret, token, Git author email, local
filesystem credential hay thông tin cá nhân không liên quan. Demo password được
nhắc trong project documentation theo `PD-SEED-001`, nhưng không cần lặp lại trong
artifact này.
