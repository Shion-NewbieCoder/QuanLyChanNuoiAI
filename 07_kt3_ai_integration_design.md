# KT3 AI Integration Design Decision Addendum

Task: TSK-KT3-02. Chế độ: DOCUMENTATION / DESIGN ONLY.

## 1. Purpose and Scope

Ghi nhận các Project Design Decision đã được con người phê duyệt cho KT3, sau audit kết luận READY WITH BLOCKERS. Đây không phải chi tiết vốn được đề bài gốc xác định, báo cáo implementation hoặc chứng nhận hoàn thành KT3.

Chỉ tạo addendum này; giữ nguyên tài liệu KT1/KT2, application source, tests, migrations và database. Không triển khai OpenAI, cài package, chạy server/seed/migration, gọi mạng hoặc tạo kết quả thử prompt trong task này.

## 2. Relationship to Previous Source-of-Truth Documents

Baseline tiếp tục theo thứ tự:

1. `Đề bài Dự Án.txt`.
2. `01_requirements_chan_nuoi_ai.md`.
3. `02_design_chan_nuoi_ai.md`.
4. `03_implementation_plan_chan_nuoi_ai_reviewed.md`.
5. `04_implementation_chan_nuoi_ai_final.md`.
6. `05_review_testing_chan_nuoi_ai_final.md`.
7. `06_final_delivery_chan_nuoi_ai_final.md`.
8. Source thực tế.
9. README/CONTEXT chỉ hỗ trợ, không chứng minh implementation đã hoàn tất.

Addendum chỉ supersede item AI-specific unresolved/conflicting được chỉ rõ dưới đây. Không đổi baseline đối với phần khác, không viết lại lịch sử KT1/KT2 hoặc diễn giải PASS trước đây thành live AI đã hoạt động.

| Baseline / audit item | Phạm vi quyết định mới |
|---|---|
| Requirements `OQ-004`; Design lựa chọn provider còn mở | `PD-KT3-AI-PROVIDER-001` giải quyết primary live provider KT3 là OpenAI; giữ abstraction. |
| Wording `first_date` / `last_date` trong yêu cầu audit KT3 | `PD-KT3-GROWTH-METRICS-001` xác nhận public names hiện hữu, không rename. |
| Design `AI-005`; prompt hiện gắn trong services | `PD-KT3-PROMPT-001` bổ sung separation, không đổi business semantics. |
| `ERR-002` có nhóm lỗi AI nhưng source/tests hiện dùng `internal_error` | `PD-KT3-AI-ERROR-001` chốt safe categories cho implementation KT3 tương lai; HTTP mappings chưa chốt. |
| KT3 yêu cầu xử lý dữ liệu dài; approved selection không cho truncate | `PD-KT3-AI-SIZE-001` chốt pre-invocation guard và từ chối rõ khi vượt giới hạn. |
| Portable loại bỏ cấu hình AI | `PD-KT3-PORTABLE-AI-001` thay định hướng này cho live demo tương lai; chưa sửa launcher. |

Traceability nền tảng: `FR-AI-001..005`, `NFR-SEC-002/003`, `NFR-REL-002`, `NFR-USAB-001`; Design `API-010/011`, `AI-001..006`, `SEC-002/002a/005/006`, `ERR-002`; Plan `TSK-019..025`, verification `TSK-028/029`. Không mở lại hoặc tuyên bố đã chạy lại task KT2.

## 3. Approved KT3 Decisions

Tất cả các quyết định sau là APPROVED PROJECT DESIGN DECISION, chưa phải implementation evidence.

| Decision ID | Quyết định | Chi tiết / traceability |
|---|---|---|
| `PD-KT3-AI-PROVIDER-001` | OpenAI primary; official SDK sau existing interface/orchestrator; server-side config, configurable model; giữ fake providers. | Mục 5; OQ-004, AI-001, SEC-005, TSK-020. |
| `PD-KT3-AI-SCOPE-001` | Chỉ Reminder, Herd Summary, Growth Report; giữ sources/allowlists/thresholds/RBAC/transient output. | Mục 4, 14; ba PD-AI feature contracts, TSK-021..023. |
| `PD-KT3-GROWTH-METRICS-001` | Existing public metric names là canonical; không rename API/UI/source/tests. | Mục 4.3; PD-AI-GROWTH-001, API-010. |
| `PD-KT3-PROMPT-001` | Tách system/user prompts, structured data, output constraints, version; free text là data. | Mục 6, 7; AI-005, TSK-024. |
| `PD-KT3-AI-ERROR-001` | Safe AI-specific categories, friendly Vietnamese UI, không raw provider exceptions; mappings để planning. | Mục 8; API-011, ERR-002. |
| `PD-KT3-AI-SIZE-001` | Deterministic configurable guard; quá lớn không gọi provider, không silent truncation. | Mục 9; giữ approved feature selection. |
| `PD-KT3-PORTABLE-AI-001` | Portable vẫn là demo entry point; kế thừa external config, không bundle key; core chạy khi AI chưa cấu hình. | Mục 12. |
| `PD-KT3-AI-TEST-001` | Regression dùng fake/mock/injected providers; live smoke riêng, opt-in. | Mục 11; test strategy TSK-020..024, 028/029. |
| `PD-KT3-PROMPT-EVAL-001` | Ít nhất ba vòng thử prompt/model thật, có human evaluation/cải tiến; không bịa evidence. | Mục 13; KT3 criterion 4. |
| `PD-KT3-AI-RBAC-001` | Giữ role matrix và precedence; không ownership/tenant/farm/per-user partitioning. | Mục 10; PD-ROLE-001, SEC-006, TSK-019. |

## 4. Existing AI Feature Contracts Preserved

Giữ `PD-AI-REMINDER-001`, `PD-AI-HERD-SUMMARY-001`, `PD-AI-GROWTH-001` và `API-010`. Không thêm route. Success envelope vẫn có `status = success`, `feature`, `result`, `notice`; result có text/source_count, thêm metrics cho Growth Report. Notice giữ ý nghĩa feature và cảnh báo AI tham khảo.

Output transient: không persist AIRequest/AIResponse, prompt, report, history hoặc provider output. Không mutate business records. Application là source of truth cho facts, source_count, classifications và metrics.

### 4.1. AI Reminder

- `POST /api/ai/reminders`; feature `reminders`.
- Scope bắt buộc `all | herd`; target_id bắt buộc và Herd tồn tại khi scope=herd, null/omitted khi scope=all.
- start_date/end_date ISO tùy chọn độc lập; nếu cùng có thì start <= end. Filter inclusive trên scheduled_date; không range thì lấy mọi qualifying record.
- Chỉ VaccineSchedule; exclude completed/cancelled. Fields: target_id, vaccine, scheduled_date, status, alert_classification.
- Derived classification theo calendar current date: overdue nếu ngày lịch < hôm nay; due today nếu bằng; due soon nếu hôm nay < ngày lịch <= hôm nay + 7 ngày; scheduled-not-yet-due nếu xa hơn. Không đổi persisted statuses `scheduled`, `due`, `completed`, `cancelled` hoặc thêm transition.
- Không qualifying records: HTTP 200, text rỗng, source_count 0, notice `No qualifying reminder data.` kèm cảnh báo chung; không gọi provider.
- Không tạo CareSchedule; không dùng CareLog/FeedRecord/MedicineRecord làm lịch chăm sóc. Care reminder vẫn deferred theo baseline.

### 4.2. AI Herd Summary

- `POST /api/ai/herd-summary`; feature `herd_summary`; herd_id bắt buộc, Herd tồn tại.
- Không date filters; lấy toàn bộ approved related records của Herd, không latest-N. VaccinationRecord được chọn qua schedules của Herd đó.

| Source | Exact field allowlist |
|---|---|
| Herd | id, code, name, animal_type, management_mode, quantity, status |
| CareLog | recorded_at, activity, notes |
| FeedRecord | recorded_at, feed_type, quantity, notes |
| MedicineRecord | recorded_at, medicine, dose, notes |
| VaccineSchedule | vaccine, scheduled_date, status |
| VaccinationRecord | actual_date, notes |

- Source_count tổng related records cung cấp, không tính Herd.
- Exclude GrowthRecord, ReproductionRecord, SaleRecord, CostRecord, HerdLossRecord, statistics, reminder output và user/auth/group data.
- Empty related data vẫn đi qua provider với Herd facts và lists rỗng; success HTTP 200, source_count 0 khi provider thành công. Prompt yêu cầu nêu related data unavailable, không bịa. Lỗi config/provider vẫn xử lý theo error model, không fake success.
- Success notice giữ `AI-generated summary based on recorded herd data.` cùng cảnh báo chung.

### 4.3. AI Growth Report

- `POST /api/ai/growth-report`; feature `growth_report`; herd_id bắt buộc, Herd tồn tại.
- start_date/end_date ISO tùy chọn độc lập, start <= end khi cùng có; filter inclusive theo measurement_date. Không range thì lấy toàn bộ GrowthRecords của Herd.
- Chỉ gửi Herd id/code/name; GrowthRecord measurement_date/weight/notes; deterministic metrics. Không thêm nguồn khác.
- Records tăng dần theo measurement_date; giữ tie-break pk hiện có, không thêm aggregation/latest-N.
- Canonical metric keys theo `PD-KT3-GROWTH-METRICS-001`:

```text
record_count
first_measurement_date
last_measurement_date
first_weight
last_weight
absolute_change
percent_change
average_weight
```

- first_date/last_date là conceptual wording trước đây, không yêu cầu rename source/API/UI/test keys.
- Với >=2 records: absolute_change = last_weight - first_weight; percent_change = (absolute_change / first_weight) * 100 khi first_weight > 0, ngược lại null. Average_weight = sum(weight) / record_count khi count > 0. AI không tính lại/override metrics.
- 0 records: record_count 0, các measurement/change/average metrics null. 1 record: first/last cùng record, average bằng weight, change metrics null.
- 0/1 record: HTTP 200, text rỗng, source_count bằng record_count, metrics khả dụng, notice `Insufficient growth data to generate an AI growth report.` kèm cảnh báo; không gọi provider.
- >=2 records: qua orchestrator/provider nếu config/guard hợp lệ; success notice `AI-generated growth report based on recorded growth data.` kèm cảnh báo. Không forecasting/prediction/diagnosis/treatment.

## 5. OpenAI Integration Boundary

`PD-KT3-AI-PROVIDER-001` giữ existing provider interface và AIOrchestrator. OpenAI là concrete adapter dùng official OpenAI Python SDK, không gọi SDK từ views hoặc feature services. Fake/injected providers tiếp tục dùng được. Đây là kiến trúc tương lai, không phải adapter đã tồn tại.

Luồng: UI/API -> permission/validation -> approved data selection -> deterministic processing -> prompt preparation/size guard -> AIOrchestrator -> adapter/SDK -> normalized output/error -> safe presentation.

Responses API tiếp tục là hướng ưu tiên trong yêu cầu audit KT3 đã duyệt; không chốt method/schema SDK chi tiết hoặc literal model ID trong task này.

| Future configuration | Ý nghĩa |
|---|---|
| `AI_PROVIDER` | Chọn adapter; primary live provider KT3 là OpenAI. |
| `OPENAI_API_KEY` | Key chỉ ở server-side external environment/configuration. |
| `OPENAI_MODEL` | Model configurable; giá trị cụ thể chờ xác nhận. |

`AI_API_KEY` là tên generic hiện có ở KT2. Contract OpenAI tương lai dùng `OPENAI_API_KEY`; không tự định nghĩa fallback/alias/precedence giữa hai tên và không phá fake/injected provider seam. Không sửa configuration hoặc .env.example trong task này.

Không hard-code/commit/bundle key, không gửi key vào prompt/browser/response. Missing AI configuration không được ngăn normal livestock-management features khởi động/hoạt động. Adapter registration, payload/response mapping và dependency triển khai sau; timeout/size configuration phải được chốt trước provider implementation.

## 6. Prompt Architecture

`PD-KT3-PROMPT-001` yêu cầu tách rõ:

1. System prompt: role, grounding và safety chung.
2. Feature-specific user prompt: nhiệm vụ presentation của từng feature.
3. Structured source/context data: chỉ approved facts và application metrics.
4. Output constraints: giữ dates/weights/status/metrics, nêu giới hạn, không sinh nghiệp vụ mới.
5. Prompt version identifier: truy vết definitions và evaluation rounds.

Prompt definitions tách khỏi business data-selection logic. Adapter không tự query DB hoặc chọn nguồn bổ sung. Giữ provider/orchestrator boundary; representation cụ thể thuộc planning. Không general chatbot, không arbitrary user-written prompts tới provider. Task này không tạo prompt code/files.

## 7. Safety and Grounding Rules

- Chỉ supplied source facts; reference/support only.
- Không diagnose disease, không thay veterinarian/livestock engineer, không treatment recommendation hoặc disease prediction.
- Không invent missing facts; nêu limitations khi insufficient evidence.
- Free-text source fields như notes/activity là DATA, không là trusted instructions và không được override system/feature constraints.
- Application giữ facts/metrics/source_count/classifications; AI không mutate Herd/GrowthRecord hoặc bất kỳ business record nào.
- Output được nhận diện là gợi ý AI, có warning, safe rendering; dữ liệu nghiệp vụ là authoritative source.
- Giữ output validation/safety boundary. Không tuyên bố prompt instruction bảo đảm model luôn tuân thủ; phải kiểm chứng sau, không tự thêm moderation taxonomy/veterinary rules.

## 8. Error and Failure Model

`PD-KT3-AI-ERROR-001` yêu cầu tối thiểu các conceptual categories riêng biệt:

- AI configuration unavailable.
- Provider timeout.
- Provider rate limit.
- Provider/network failure.
- Invalid/empty provider response.
- Unsupported/invalid model configuration.
- AI input too large.

Đây chưa phải literal error_code hoặc HTTP mapping. Exact mappings được xác định trong implementation planning, không chọn HTTP status cụ thể ở đây. Giữ existing HTTP 200 empty/insufficient-data contracts tại mục 4.

Không raw API key, raw provider payload hoặc sensitive exception text trong browser/API response. UI phải có friendly Vietnamese messages. Secret-safe verification phải xét logs/exception chains, không chỉ response. AI failure không ngăn core management; không dùng fake success để che lỗi. Source/tests hiện dùng generic internal_error chưa được thay đổi trong task này.

## 9. Data Size Handling

`PD-KT3-AI-SIZE-001`: giữ approved selection, không silently truncate hoặc chọn latest-N, không đổi source_count để che records bị bỏ.

Trước provider invocation có deterministic configurable guard trên prepared AI payload. Vượt guard: provider KHÔNG được gọi; người dùng nhận safe explicit result/error nghĩa là Dữ liệu quá lớn để xử lý bằng AI; business data không thay đổi. HTTP mapping để planning.

Không chọn numeric threshold, đơn vị/thuật toán đo cụ thể ở đây; cách đo deterministic được chốt cùng size parameter theo model/implementation trước triển khai. Guard không trở thành business filter. Các nhánh không cần provider (Reminder không nguồn; Growth 0/1) giữ nguyên mục 4.

## 10. RBAC and Data Access

`PD-KT3-AI-RBAC-001` giữ `PD-ROLE-001`:

| Role | AI access |
|---|---|
| quản lý | allowed |
| kỹ thuật viên | allowed |
| nhân viên | denied |
| Authenticated không có recognized role | denied |

Precedence `quản lý > kỹ thuật viên > nhân viên`: một effective role ưu tiên cao nhất quyết định quyền, không union/intersection. Không dựa unordered .first() hoặc Group PK.

Giữ role-wide data access và feature-specific selection/allowlists; không thêm ownership, tenant, farm scope hoặc per-user partitioning. Kiểm tra server-side, không chỉ ẩn UI. Không gửi user/auth/group data tới provider.

## 11. Test Strategy

`PD-KT3-AI-TEST-001`: normal automated regression không phụ thuộc real OpenAI API calls. Fake/mock/injected providers kiểm tra request/response mapping, timeout, rate limit, provider failure, invalid/empty output, size guard, secret-safe errors/logs, permissions và feature semantics.

Giữ tests requested-Herd isolation, exact allowlists, date boundaries, deterministic metrics, empty/minimum-data branches, transient/no-mutation, warning/escaping và core management khi AI unavailable. Vượt size guard phải assert provider không được gọi.

Live OpenAI verification là opt-in/manual smoke riêng, chỉ khi có valid external credentials/network; là KT3 evidence, không là dependency của regression. Không sửa/chạy tests hoặc ghi PASS cho tests tương lai trong task này.

## 12. Portable Demo Strategy

`PD-KT3-PORTABLE-AI-001`: portable vẫn là intended convenient demo entry point. Current tools/portable_demo.py xóa AI_PROVIDER/AI_API_KEY là finding chưa sửa, không phù hợp KT3 live AI.

Future runtime được kế thừa external AI configuration ở mục 5. Không real key trong submitted project, DEMO.exe hoặc Git. Không config: core app vẫn chạy và AI UI báo live AI chưa được cấu hình. Có valid external config: cùng portable application dùng được live OpenAI.

Launcher/build/runtime verification thuộc task implementation sau; không sửa portable_demo.py, build EXE hoặc chạy demo ở đây.

## 13. KT3 Evidence Strategy

`PD-KT3-PROMPT-EVAL-001` yêu cầu ít nhất 3 vòng thử prompt/model THẬT. Mỗi vòng sau này ghi feature, prompt version, configured model, representative source data, output, observed issue, human evaluation và change made for next round. Nếu chưa có vòng tiếp theo, ghi trung thực trạng thái thay đổi; không bịa cải tiến/kết quả.

Không API keys, secrets hoặc unnecessary personal/sensitive data trong evidence. Representative data/output phải truy vết được, không trình bày fake invocation như live. Evidence evaluation có kiểm soát không tạo product AI history/persistence.

AI_CODING_EVIDENCE.md từ KT2 tái sử dụng cho review/debug/refactor evidence, không thay ba vòng product prompt/model trials. Historical regression reports không thay current/live verification. Task này không tạo trial outputs hoặc tuyên bố KT3 criteria complete.

## 14. Explicitly Out of Scope

- Diagnosis, treatment, disease prediction, forecasting, autonomous veterinary advice.
- General chatbot/arbitrary prompts, additional product AI features/business entities.
- New roles/databases/frontend frameworks, ownership/tenant/farm partitioning.
- Đổi approved sources/allowlists/thresholds/formulas, metric renaming, AI persistence/business automation.
- Source/test/config/launcher changes, packages, migrations, seed, server, network/live AI calls trong task này.
- Viết lại baseline documents/README, fabricate trial evidence hoặc commit secrets.

## 15. Remaining Implementation Parameters

Chỉ bốn implementation parameters còn mở; không phải unresolved business rules:

| Parameter | Trạng thái và gate |
|---|---|
| Exact OpenAI model ID | CHƯA XÁC NHẬN; xác nhận riêng trước provider implementation, không literal default ở đây. |
| Exact timeout value | CHƯA XÁC NHẬN; chốt configuration/value trước provider implementation. |
| Exact input-size threshold | CHƯA XÁC NHẬN; chốt cùng deterministic measurement phù hợp model/implementation, không truncate. |
| Exact HTTP status mappings cho AI errors | CHƯA XÁC NHẬN; chốt trong planning trước khi đổi error behavior/tests. |

Không chọn ngầm các giá trị này. Design readiness không bỏ qua các parameter gates hoặc cấp phép implementation/live calls trong task hiện tại.

## 16. Audit Findings Deferred to Later Tasks

- Authentication alignment — NON-BLOCKING: DRF hiện kế thừa defaults có BasicAuthentication và SessionAuthentication, trong khi tài liệu thường mô tả Session Authentication. Ghi cho focused security/configuration alignment task; không kết luận authorization bypass, không sửa settings hoặc quyết định bỏ BasicAuthentication ở đây.
- Live adapter/registration/SDK/model config chưa có; không tuyên bố chỉ đặt key là chạy được.
- Prompt separation, size guard, AI-specific errors và portable config vẫn là implementation gaps: policy đã chốt ở đây, source chưa đổi.
- Provider factory exception chaining/logger.exception cần secret-safe verification khi thêm adapter; không tuyên bố có real secret leak đã được chứng minh.
- Test/live evidence gaps phải được kiểm chứng sau implementation, không lấy historical KT2 PASS làm kết quả KT3 mới.

## 17. Implementation Readiness Checklist

- [x] Đủ 10 approved decision IDs và phạm vi supersession, không rewrite KT2 history.
- [x] OpenAI đã chọn; không tự chọn literal model ID.
- [x] Giữ ba feature contracts, canonical metrics, sources, RBAC, transient behavior.
- [x] Prompt/safety/error/size/portable/test/evaluation policy đã rõ.
- [x] Không unresolved business-rule decision trong phạm vi addendum.
- [x] Bốn implementation parameters vẫn mở tường minh; auth finding NON-BLOCKING.
- [ ] Xác nhận parameters trước implementation tương ứng.
- [ ] Triển khai adapter/prompt/error/size/portable trong các task sau được phép.
- [ ] Automated verification, opt-in live smoke, ba vòng trial thật: chưa có kết quả trong task này.

Trạng thái bên dưới chỉ xác nhận THIẾT KẾ sẵn sàng làm baseline KT3, không khẳng định adapter đã hoạt động, không bỏ qua parameter gates, không tuyên bố KT3 hoàn tất hoặc thay đổi lịch sử KT2.

STATUS: DESIGN READY FOR KT3 IMPLEMENTATION
