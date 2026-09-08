# 03 Implementation Plan

## Role

Bạn là Technical Lead chịu trách nhiệm chuyển thiết kế đã được duyệt thành kế hoạch triển khai có thể thực thi cho **Hệ thống quản lý chăn nuôi có tích hợp AI**.

## Objective

Chia thiết kế ở `docs/02_design.md` thành các task triển khai có thứ tự, dependency, Definition of Done, chiến lược kiểm thử/xác minh và traceability. Bước này **không viết source code**.

## Language

- Toàn bộ nội dung viết bằng tiếng Việt có dấu, mã hóa UTF-8.
- Giữ nguyên tiếng Anh hoặc ký hiệu kỹ thuật đối với tên file, thư mục, command, endpoint, ID, status marker và code block.

## Inputs

- `docs/01_requirements.md`
- `docs/02_design.md`
- `prompts/01_requirements.md`
- `prompts/02_design.md`

### Gate đầu vào

`docs/01_requirements.md` và `docs/02_design.md` đã đạt `STATUS: PASS` theo hai quality gate trước. Vì vậy kế hoạch này được phép chuyển sang bước Implementation.

## Skills.sh Evidence

| Skill | Nhiệm vụ áp dụng | Đầu ra đã dùng | Vị trí bằng chứng |
|---|---|---|---|
| `tdd` | Gắn mỗi task với test hoặc verification command; ưu tiên kiểm thử đơn vị cho rule và smoke/integration test cho API/luồng chính | Test strategy, test plan và verification command cho từng task | `Task List`, `Test Plan`, `Dependency Matrix` |
| `django-expert` | Lập thứ tự Django theo dependency: project/settings -> apps/models -> migrations -> services -> views/API -> templates -> tests | Thứ tự task backend và dependency migration/model/service/view | `Task List`, `Dependency Matrix` |
| `codebase-design` | Giữ ranh giới theo các component đã duyệt trong Design | Mỗi task có module/ownership và Design ID tương ứng | `Task List`, `Traceability` |
| `frontend-design` | Lập kế hoạch dashboard Bootstrap 5 và frontend scaffold, bao phủ state, feedback và accessibility checks | UI task có verification cho loading/error/empty state và semantic form/table | `Task List`, `Test Plan` |
| `django-security` | Lập task cho authentication, authorization, CSRF, validation, secret handling và safe errors | Security tasks và verification commands | `Task List`, `Dependency Matrix`, `Test Plan` |

## Scope

- Chia task backend, database, API, dashboard, frontend scaffold, AI, tests, security và documentation.
- Xác định dependency và thứ tự thực hiện.
- Xác định task có thể chạy song song.
- Xác định test-first hoặc verification-first strategy.
- Xác định verification command.
- Định nghĩa Definition of Done cho từng task.
- Tạo traceability `Requirement -> Design Component -> Implementation Task`.

## Out of Scope

- Không viết source code trong bước 03.
- Không sửa requirements/design; nếu phát sinh sai lệch phải ghi nhận backtrack về bước SDLC tương ứng.
- Không thêm nghiệp vụ ngoài `docs/01_requirements.md` và `docs/02_design.md`.
- Không tạo API key thật, dữ liệu thật hoặc triển khai production trong bước planning.

## Technology Baseline

Các quyết định này được lấy từ Design đã duyệt, không phải requirement mới:

| Hạng mục | Quyết định |
|---|---|
| Backend | Django + Django REST Framework |
| Database | SQLite cho bản thực hành |
| Dashboard | Django Templates + Bootstrap 5 |
| Frontend scaffold | Vite/React ở mức scaffold |
| AI | Adapter-based; provider cấu hình qua environment/configuration |
| Authentication | Django authentication + session |
| API | JSON API cùng origin, DRF |

## Implementation Strategy

Thứ tự tổng quát:

```text
Setup project
  -> Settings / environment
  -> Models / migrations
  -> Authentication / authorization
  -> Domain services / validation
  -> CRUD APIs
  -> Statistics APIs
  -> AI orchestration / AI features
  -> Dashboard
  -> Frontend scaffold
  -> Tests / security verification
  -> Seed demo data
  -> README / run verification
```

Nguyên tắc:

1. Không xây API trước khi model và business validation ổn định.
2. Không xây AI trước khi các dữ liệu đầu vào nghiệp vụ đã có API/domain service ổn định.
3. Dashboard chỉ đọc các nguồn dữ liệu đã có contract rõ ràng.
4. Test rule nghiệp vụ trước hoặc đồng thời với implementation task tương ứng.
5. Khi phát hiện requirement/design không đủ để triển khai, dừng task và backtrack thay vì tự thêm nghiệp vụ.

## Task List

| Task ID | Requirement ID | Design ID | Objective | Dependencies | Files | Tests | Verification | Definition of Done |
|---|---|---|---|---|---|---|---|---|
| TSK-001 | NFR-TECH-001 | TD-001..TD-005, ARCH-001 | Khởi tạo skeleton project đúng technology baseline | Không | `backend/`, `frontend/`, `README.md`, `.gitignore` | Kiểm tra cấu trúc thư mục và môi trường | `python --version`, `node --version`, `npm --version`; sau khi cài backend dependency, `python -m django --version` | Project tạo đúng cấu trúc; dependency được ghi; không có secret thật |
| TSK-002 | NFR-SEC-002, NFR-TECH-001 | SEC-005, TD-005 | Thiết lập environment/configuration cho secret và provider | TSK-001 | `backend/.env.example`, settings/config files | Kiểm tra secret không hard-code | `git grep -nE "(sk-|AIza|api[_-]?key)" -- .` với mẫu kiểm tra phù hợp; khởi động bằng `.env.example` | Không có secret thật trong source; provider config đọc từ environment |
| TSK-003 | NFR-REL-001 | ARCH-001, DOMAIN-001, DOMAIN-004 | Cấu hình Django settings, database và base app structure | TSK-001, TSK-002 | `backend/config/*`, app configs | Smoke test Django startup | `python manage.py check` | Django khởi động, SQLite cấu hình đúng, không lỗi system check |
| TSK-004 | FR-AUTH-001, FR-AUTH-002, NFR-SEC-001 | DES-MOD-001, SEC-001, SEC-002, API-002 | Thiết lập authentication và role model/permission | TSK-003 | auth app / user config / permission files | Auth unit/integration tests | `python manage.py test` nhóm auth | Login hợp lệ thành công; sai thông tin bị từ chối; role được kiểm tra |
| TSK-005 | FR-HERD-001, FR-HERD-002, FR-PEN-001, NFR-REL-001 | DES-MOD-002, DES-MOD-003, DOMAIN-001..004 | Tạo domain model cho Herd, Animal, AnimalGroup, Pen | TSK-003, TSK-004 | `apps/herds/`, `apps/pens/`, migrations | Model validation tests | `python manage.py makemigrations --check`, `python manage.py migrate`, test model | Model và quan hệ logic được cài đặt đúng Design; migration chạy thành công |
| TSK-006 | FR-CARE-001, FR-FEED-001, FR-MED-001, NFR-REL-001 | DES-MOD-004, DOMAIN-001, DOMAIN-004 | Tạo domain model cho nhật ký chăm sóc, thức ăn, thuốc | TSK-005 | `apps/care/` hoặc module tương ứng, migrations | Validation tests cho bản ghi nghiệp vụ | `python manage.py test` nhóm care | Bản ghi lưu/đọc đúng, tham chiếu đối tượng hợp lệ |
| TSK-007 | FR-VAX-001, FR-ALERT-001 | DES-MOD-005, DOMAIN-001..004 | Tạo model lịch vaccine và bản ghi tiêm | TSK-005 | `apps/vaccinations/`, migrations | Tests cho lịch, trạng thái và ngày đến hạn | `python manage.py test` nhóm vaccination | Lịch vaccine và kết quả tiêm được lưu/đọc; trạng thái nhất quán |
| TSK-008 | FR-GROW-001, FR-REPRO-001 | DES-MOD-006, DOMAIN-001..004 | Tạo model tăng trưởng và sinh sản | TSK-005 | `apps/growth/`, `apps/reproduction/`, migrations | Tests cho weight/date và event | `python manage.py test` nhóm growth/reproduction | Dữ liệu cân nặng, tăng trưởng và sinh sản lưu/đọc đúng |
| TSK-009 | FR-SALE-001, FR-REV-001 | DES-MOD-007, DOMAIN-001, DOMAIN-004 | Tạo model xuất bán và doanh thu | TSK-005 | `apps/sales/`, migrations | Tests cho sale amount và target | `python manage.py test` nhóm sales | Sale record hợp lệ; doanh thu có nguồn từ sale record |
| TSK-010 | FR-AUTH-001..FR-REV-001, NFR-REL-001 | DES-MOD-002..008, DOMAIN-004 | Tạo domain services và validation rules tập trung | TSK-005..TSK-009 | `services.py`, validators, domain helpers | Unit tests business rules | `python manage.py test` domain/service suites | Validation không phụ thuộc trực tiếp vào UI; invariant được bảo vệ |
| TSK-011 | FR-HERD-001, FR-HERD-002 | DES-MOD-002, API-003 | Xây CRUD API cho đàn/cá thể/nhóm | TSK-004, TSK-005, TSK-010 | `urls.py`, serializers, views, tests cho herd API | API CRUD tests | `python manage.py test` API herd; smoke bằng client HTTP | CRUD đúng quyền, dữ liệu hợp lệ, error contract đúng |
| TSK-012 | FR-PEN-001 | DES-MOD-003, API-004 | Xây CRUD API cho chuồng | TSK-004, TSK-005, TSK-010 | `apps/pens/` | API tests | `python manage.py test` API pen | CRUD và permission đúng; liên kết đàn hợp lệ |
| TSK-013 | FR-CARE-001, FR-FEED-001, FR-MED-001 | DES-MOD-004, API-005 | Xây API cho chăm sóc, thức ăn, thuốc | TSK-004, TSK-006, TSK-010 | `apps/care/` | CRUD/create/read validation tests | `python manage.py test` API care | Bản ghi tạo/đọc đúng; input sai trả lỗi có cấu trúc |
| TSK-014 | FR-VAX-001, FR-ALERT-001 | DES-MOD-005, API-006 | Xây API vaccine và dữ liệu lịch cần nhắc | TSK-004, TSK-007, TSK-010 | `apps/vaccinations/` | Tests lịch quá hạn/sắp hạn/đã tiêm | `python manage.py test` API vaccination | CRUD lịch và kết quả tiêm đúng; dữ liệu lịch nhắc truy xuất được |
| TSK-015 | FR-GROW-001, FR-REPRO-001 | DES-MOD-006, API-007 | Xây API tăng trưởng và sinh sản | TSK-004, TSK-008, TSK-010 | `apps/growth/`, `apps/reproduction/` | API + validation tests | `python manage.py test` growth/reproduction | Tạo/đọc dữ liệu đúng; dữ liệu biên bị từ chối phù hợp |
| TSK-016 | FR-SALE-001, FR-REV-001 | DES-MOD-007, API-008 | Xây API xuất bán và doanh thu | TSK-004, TSK-009, TSK-010 | `apps/sales/` | API tests sale/revenue | `python manage.py test` sales | Xuất bán và doanh thu được lưu/tra cứu đúng |
| TSK-017 | FR-STAT-001, FR-STAT-002, FR-STAT-003 | DES-MOD-008, DOMAIN-001..004, API-009 | Xây source-data tối thiểu, service/query và API thống kê | TSK-006, TSK-008, TSK-009 | statistics service/views/urls, `HerdLossRecord`/`CostRecord` models và migrations | Tests persistence, validation và dữ liệu tổng hợp | `python manage.py test` statistics; `python manage.py makemigrations --check` | Có thể lưu nguồn dữ liệu `HerdLossRecord`/`CostRecord` tối thiểu và lấy thống kê tăng trưởng, chi phí, hao hụt theo Design đã phê duyệt |
| TSK-018 | NFR-REL-002 | API-011, ERR-001..003 | Chuẩn hóa error contract, logging và safe errors | TSK-010..TSK-016 | common error handlers, logging config, API utilities | Tests lỗi 400/403/404/500 dự kiến | `python manage.py test` error suites; manual invalid requests | Input/permission/server/AI errors không làm ứng dụng crash; không lộ stack trace/secret |
| TSK-019 | NFR-SEC-001, NFR-SEC-002, NFR-SEC-003 | SEC-001..SEC-008, PD-ROLE-001 | Hoàn thiện security controls, resolve deterministic effective role và thực thi matrix quyền đã phê duyệt trên mọi API hiện có | TSK-002, TSK-004, TSK-010, TSK-018 | auth/permission, settings, forms, AI boundaries | Security-focused tests theo `PD-ROLE-001`, gồm mọi tổ hợp multi-role và no-role | `python manage.py test`; grep secret; kiểm thử CSRF/permission | Role enforcement theo matrix và precedence `quản lý > kỹ thuật viên > nhân viên`, no-role denial, secret handling, CSRF, XSS-safe rendering và role-wide data scope đều được kiểm tra; AI chỉ chuẩn bị boundary, không triển khai TSK-020+ |
| TSK-020 | FR-AI-004, NFR-SEC-003 | DES-MOD-009, AI-001, SEC-006, PD-ROLE-001 | Tạo AI orchestration layer và provider adapter boundary | TSK-002, TSK-010, TSK-019 | `apps/ai/`, provider adapter/config | Unit tests bằng mock provider và AI role access | `python manage.py test` AI adapter/orchestrator | AI layer không phụ thuộc UI; provider có thể thay bằng adapter; quản lý/kỹ thuật viên được phép, nhân viên bị từ chối, dữ liệu đầu vào theo quyền |
| TSK-021 | FR-AI-001, FR-ALERT-001 | AI-002, API-010, PD-AI-REMINDER-001 | Triển khai AI vaccine reminder transient qua `POST /api/ai/reminders` | TSK-014, TSK-020 | AI service/serializer/view | Mock AI + request/permission/empty-data tests | `python manage.py test` AI reminder | Chỉ `VaccineSchedule` qualifying được gửi; empty data không gọi provider; không tạo CareSchedule, persistence, hoặc TSK-022..024 behavior |
| TSK-022 | FR-AI-002 | AI-003, API-010, PD-AI-HERD-SUMMARY-001 | Triển khai herd summary transient qua `POST /api/ai/herd-summary` | TSK-006, TSK-011, TSK-020 | AI service/view | Tests allowlist, empty data, permission/output | `python manage.py test` herd summary | Chỉ Herd/care/feed/medicine/vaccination data allowlisted; no filters/truncation/persistence/mutation; Growth reserved TSK-023 |
| TSK-023 | FR-AI-003, FR-GROW-001 | AI-004, API-010, PD-AI-GROWTH-001 | Triển khai Growth Report transient với deterministic metrics | TSK-008, TSK-017, TSK-020 | AI service/view | Tests filters, metrics, threshold, permission/output | `python manage.py test` growth report | Inclusive filters; 0/1 record không gọi provider; >=2 gọi orchestrator; không prediction/forecasting/persistence; TSK-024 giữ riêng |
| TSK-024 | FR-AI-005, NFR-USAB-001 | AI-005, AI-006, UI-003 | Chuẩn hóa prompt boundary, output validation và safety notice | TSK-021..TSK-023 | prompt/config files, AI validators, templates/components | Tests malformed/empty/unsafe output | `python manage.py test` AI validation | Output không hợp lệ bị từ chối/xử lý; safety notice hiển thị rõ |
| TSK-025 | FR-STAT-001, FR-STAT-002, FR-STAT-003, NFR-USAB-001 | DES-MOD-010, UI-001, UI-002, UI-003 | Xây dashboard Django + Bootstrap 5 | TSK-011..TSK-018, TSK-024 | templates, static/css, dashboard views | Template/view tests; UI smoke checklist | `python manage.py test`; manual browser smoke | Dashboard hiển thị dữ liệu thống kê, trạng thái loading/empty/error phù hợp; phân biệt AI và dữ liệu gốc |
| TSK-026 | NFR-USAB-001, NFR-TECH-001 | TD-004, UI-001..003 | Tạo frontend Vite/React scaffold đúng phạm vi Design | TSK-001, TSK-025 | `frontend/` scaffold | Build check | `npm install`, `npm run build` | Scaffold build thành công; không triển khai CRUD/API thật ngoài phạm vi |
| TSK-027 | FR-AUTH-001..FR-REV-001, FR-AI-001..005 | API-003..010, UI-001..003, PD-SEED-001 | Tạo local-only deterministic demo dataset qua duy nhất `seed_demo` theo exact reserved accounts/counts/scenarios | TSK-011..TSK-025 | Django management command và seed tests | Exact reserved-count, domain validation, DEBUG gate, repeated-run idempotence, role restore, relative-date refresh, non-demo preservation và statistics/AI-source coverage tests | `python manage.py seed_demo`; chạy lặp; `python manage.py test` seed suite; API/dashboard smoke | DEBUG-only command tạo/restore đúng PD-SEED-001, không duplicate/flush/non-demo mutation, không precompute statistics hay persist/call AI, không schema migration |
| TSK-028 | NFR-REL-001, NFR-REL-002 | ARCH-001, ERR-001..003 | Chạy regression integration cho các luồng chính | TSK-018..TSK-027 | `tests/` | Integration/regression tests | `python manage.py test` toàn bộ backend | Các luồng login -> CRUD -> stats -> AI chạy qua dữ liệu demo ổn định |
| TSK-029 | NFR-SEC-001..003 | SEC-001..SEC-008 | Security regression cuối vòng | TSK-019, TSK-028 | security tests/docs | Permission, CSRF, secret, data-scope tests | Test suite security + manual checklist | Không còn BLOCKER/CRITICAL liên quan security trong phạm vi bài |
| TSK-030 | NFR-TECH-001, NFR-REL-001, NFR-USAB-001 | ARCH-001, UI-001, API-001..011 | Hoàn thiện README và tài liệu chạy thử | TSK-028, TSK-029 | `README.md`, `.env.example`, docs | Documentation/runbook check | Thực hiện toàn bộ lệnh cài đặt/chạy/seed từ README trên môi trường sạch | Người khác có thể dựng môi trường và chạy demo theo README; endpoint/command khớp thực tế |

## Dependency Matrix

| Task ID | Depends On | Reason | Can Run In Parallel | Blocking Risk |
|---|---|---|---|---|
| TSK-001 | — | Tạo workspace cơ sở | Có thể song song chuẩn bị tài liệu | Sai toolchain làm toàn bộ plan dừng |
| TSK-002 | TSK-001 | Cần skeleton để đặt config | Với TSK-003 sau khi settings đã có | Lộ secret hoặc config sai |
| TSK-003 | TSK-001, TSK-002 | Cần project và environment | Không nên song song với migration | Django không start |
| TSK-004 | TSK-003 | Cần Django settings | Có thể song song thiết kế test | Permission sai ảnh hưởng toàn hệ thống |
| TSK-005 | TSK-003, TSK-004 | Domain cần auth context và DB | Không nên song song với TSK-006..009 nếu dùng cùng migration boundary | Domain schema sai gây backtrack Design |
| TSK-006 | TSK-005 | Care record tham chiếu domain | Có thể song song với TSK-007..009 sau khi TSK-005 pass | Quan hệ sai |
| TSK-007 | TSK-005 | Vaccine tham chiếu domain | Có thể song song với TSK-006, TSK-008, TSK-009 | Rule lịch sai |
| TSK-008 | TSK-005 | Growth/reproduction tham chiếu domain | Có thể song song với TSK-006, TSK-007, TSK-009 | Dữ liệu tăng trưởng sai |
| TSK-009 | TSK-005 | Sale tham chiếu domain | Có thể song song với TSK-006..008 | Doanh thu không nhất quán |
| TSK-010 | TSK-005..009 | Service cần đầy đủ model | Sau khi từng model pass | Business invariant phân tán |
| TSK-011 | TSK-004,005,010 | API cần auth + model + validation | Có thể song song với TSK-012,013 sau prerequisites | Contract không ổn định |
| TSK-012 | TSK-004,005,010 | API pen | Có thể song song với TSK-011,013 | Liên kết pen/herd sai |
| TSK-013 | TSK-004,006,010 | API care | Có thể song song với TSK-011,012 | Bản ghi nghiệp vụ sai |
| TSK-014 | TSK-004,007,010 | API vaccine | Có thể song song với TSK-011..013 | Logic lịch ảnh hưởng AI |
| TSK-015 | TSK-004,008,010 | API growth/reproduction | Có thể song song với TSK-011..014 | Dữ liệu AI growth thiếu |
| TSK-016 | TSK-004,009,010 | API sale | Có thể song song với TSK-011..015 | Revenue mismatch |
| TSK-017 | TSK-006,008,009 | Statistics cần dữ liệu nguồn; TSK-017 tự triển khai source-data tối thiểu `HerdLossRecord`/`CostRecord` theo OQ-007/OQ-008 đã phê duyệt | Có thể song song với TSK-011..016 khi source data ổn | Số liệu sai hoặc mở rộng sang accounting/mortality management ngoài Design |
| TSK-018 | TSK-010..016 | Chuẩn hóa lỗi cho các API/service | Có thể bắt đầu sớm design tests nhưng merge sau API | Lỗi không an toàn |
| TSK-019 | TSK-002,004,010,018 | Security xuyên suốt | Có thể song song review với TSK-011..018 | Rủi ro bảo mật |
| TSK-020 | TSK-002,010,019 | AI cần config, domain service và data scope | Không chạy trước security boundary | Lộ dữ liệu/API key |
| TSK-021 | TSK-014,020 | AI reminder cần vaccine schedule | Có thể song song TSK-022, TSK-023 | Không có dữ liệu lịch |
| TSK-022 | TSK-006,011,020 | Herd summary cần care data | Có thể song song TSK-021, TSK-023 | Input AI không đầy đủ |
| TSK-023 | TSK-008,017,020 | Growth report cần growth/statistics | Có thể song song TSK-021, TSK-022 | Report thiếu dữ liệu |
| TSK-024 | TSK-021..023 | Chuẩn hóa output sau khi có feature | Có thể review song song nhưng gate trước UI final | Output AI sai/mất safety notice |
| TSK-025 | TSK-011..018,024 | Dashboard cần API và AI outputs | Có thể bắt đầu layout từ sớm nhưng integration sau prerequisites | UI phụ thuộc contract |
| TSK-026 | TSK-001,025 | Scaffold theo baseline Design | Có thể song song với backend test sau TSK-001 | Scope creep frontend |
| TSK-027 | TSK-011..025 | Seed cần schema/API/domain, AI factual-source contract và dashboard ổn định | Không chạy trước khi PD-SEED-001 được phê duyệt | Seed sai hoặc mutate non-demo data gây false test result |
| TSK-028 | TSK-018..027 | Regression cần toàn bộ luồng chính | Không song song với sửa blocker | Blocker tích lũy |
| TSK-029 | TSK-019,028 | Security regression cuối | Không song song với thay đổi security | Bỏ sót lỗ hổng |
| TSK-030 | TSK-028,029 | README phải phản ánh hệ thống cuối | Không nên hoàn thiện trước regression | Hướng dẫn chạy sai |

## Workstreams / Parallelization

Sau khi TSK-005 hoàn thành, các workstream có thể triển khai song song có kiểm soát:

```text
Backend domain:
  TSK-006 -> TSK-007 -> TSK-008 -> TSK-009 -> TSK-010

API:
  TSK-011 / TSK-012 / TSK-013 / TSK-014 / TSK-015 / TSK-016

Analytics:
  TSK-017

AI:
  TSK-020 -> TSK-021 / TSK-022 / TSK-023 -> TSK-024

UI:
  TSK-025 -> TSK-026

Quality:
  TSK-018 / TSK-019 -> TSK-028 -> TSK-029 -> TSK-030
```

Không được coi các nhánh song song là độc lập tuyệt đối: mọi task phải merge/review qua các dependency đã ghi trước khi chạy task downstream.

## Test Strategy

### 1. Test-first cho domain và validation

Ưu tiên viết test cho các rule có thể xác minh bằng dữ liệu:

- Authentication/permission.
- Liên kết đàn/cá thể/nhóm/chuồng.
- Ngày và trạng thái vaccine.
- Cân nặng và ngày đo.
- Sale và doanh thu.
- Tính thống kê tăng trưởng/chi phí/hao hụt.
- Data scope trước khi gọi AI.

### 2. API verification

Mỗi API CRUD/read endpoint phải có tối thiểu:

- Case hợp lệ.
- Case thiếu/sai dữ liệu.
- Case không có quyền.
- Case dữ liệu tham chiếu không tồn tại.
- Kiểm tra response status và JSON error contract.

### 3. AI verification

AI provider thật không được là dependency bắt buộc của unit test. Dùng mock/fake provider để kiểm tra:

- Input mapping từ dữ liệu hệ thống.
- Output schema/format.
- Response rỗng hoặc không hợp lệ.
- Provider timeout/lỗi.
- Data scope.
- Safety notice.

Manual verification với provider thật chỉ thực hiện sau khi mock tests pass và khi có cấu hình API key hợp lệ.

### 4. Dashboard/UI verification

Kiểm tra:

- Đăng nhập và hiển thị theo role.
- Dữ liệu danh sách/chi tiết.
- Empty state.
- Validation error.
- Server/API error.
- Hiển thị cảnh báo vaccine.
- Hiển thị thống kê.
- Phân biệt rõ dữ liệu gốc và gợi ý AI.
- Accessibility cơ bản: label form, keyboard focus, semantic table/button, thông báo lỗi có thể nhận biết.

### 5. Regression

Verification command backend dự kiến:

```text
python manage.py check
python manage.py makemigrations --check
python manage.py test
```

Frontend scaffold:

```text
npm run build
```

Nếu project dùng virtual environment thì mọi command Python được chạy trong environment của project.

## Test Plan by Task

| Task ID | Test Strategy | Verification |
|---|---|---|
| TSK-001 | Environment smoke | Version commands + structure check |
| TSK-002 | Secret/config check | Repository scan + start with example env |
| TSK-003 | Django system check | `python manage.py check` |
| TSK-004 | Auth/permission integration | Django test auth suite |
| TSK-005 | Model/invariant tests | `makemigrations --check`, `migrate`, model tests |
| TSK-006 | Validation/unit tests | Care/feed/medicine test suite |
| TSK-007 | Date/status rule tests | Vaccine test suite |
| TSK-008 | Numeric/date/event tests | Growth/reproduction test suite |
| TSK-009 | Sale/revenue tests | Sales test suite |
| TSK-010 | Service tests | Domain/service test suite |
| TSK-011 | CRUD/API tests | Herd endpoint tests |
| TSK-012 | CRUD/API tests | Pen endpoint tests |
| TSK-013 | API validation tests | Care/feed/medicine endpoints |
| TSK-014 | Schedule/permission tests | Vaccination endpoint tests |
| TSK-015 | Numeric/date API tests | Growth/reproduction endpoint tests |
| TSK-016 | Revenue consistency tests | Sales endpoint tests |
| TSK-017 | Persistence/validation + aggregate/query tests | Statistics suite với fixture cố định cho `HerdLossRecord`/`CostRecord`, công thức loss rate, total cost, category và lọc ngày |
| TSK-018 | Error-path tests | 400/403/404/500 scenarios |
| TSK-019 | Security regression | Permission, CSRF, secret, XSS/data-scope checks |
| TSK-020 | Mock-provider unit tests | Adapter/orchestrator tests |
| TSK-021 | AI reminder tests | Mock AI + manual provider scenario |
| TSK-022 | Herd summary tests | Mock AI + manual scenario |
| TSK-023 | Growth report tests | Mock AI + manual scenario |
| TSK-024 | Invalid output/safety tests | AI validator tests + manual UI check |
| TSK-025 | View/template/UI smoke | Django tests + browser checklist |
| TSK-026 | Build verification | `npm install`, `npm run build` |
| TSK-027 | Deterministic seed verification | DEBUG=False refusal; exact reserved counts; valid XOR/domain data; run twice without duplicates; restore demo values/roles and relative dates; preserve non-demo rows; derived statistics/revenue non-empty; factual reminder/summary/growth sources present; no AI call/output persistence |
| TSK-028 | Full regression | `python manage.py test` |
| TSK-029 | Security regression | Security tests + manual checklist |
| TSK-030 | Documentation verification | Fresh setup/run from README |

## Definition of Done Rules

Mỗi task chỉ được coi là Done khi đồng thời thỏa:

1. Implementation đúng Design ID được giao.
2. Không làm phát sinh requirement mới ngoài scope.
3. Test hoặc verification command tương ứng đã chạy và đạt.
4. Không còn lỗi blocker/critical thuộc task.
5. Dữ liệu nhạy cảm/API key không xuất hiện trong source hoặc log.
6. Nếu task thay đổi contract, tài liệu/traceability liên quan được cập nhật.
7. Kết quả có thể bàn giao cho task phụ thuộc mà không cần giả định ngầm.

## Backtrack Rule

Nếu trong bước Implementation xảy ra một trong các tình huống sau, **không tự sửa bằng cách thêm nghiệp vụ tùy ý**:

| Phát hiện | Quay lại |
|---|---|
| Requirement thiếu/mâu thuẫn | `01_requirements.md` |
| Design không thể triển khai hoặc mâu thuẫn với requirement | `02_design.md` |
| Dependency/task order sai nhưng requirements/design vẫn đúng | `03_implementation_plan.md` |
| Lỗi chỉ nằm trong code | `04_implementation.md` |
| Chức năng chạy nhưng test/quality không đạt | `05_review_testing.md` |

Sau khi backtrack, phải cập nhật traceability và re-validate stage đó trước khi tiếp tục.

## Requirement -> Design -> Implementation Traceability

| Requirement ID | Design ID | Task ID | Test Strategy |
|---|---|---|---|
| FR-AUTH-001 | DES-MOD-001, SEC-001 | TSK-004 | Auth integration test |
| FR-AUTH-002 | DES-MOD-001, SEC-002, SEC-002a, PD-ROLE-001 | TSK-004, TSK-019 | Role/permission tests theo matrix đã phê duyệt |
| FR-HERD-001 | DES-MOD-002, DOMAIN-001 | TSK-005, TSK-011 | Model + CRUD API tests |
| FR-HERD-002 | DES-MOD-002, DOMAIN-001 | TSK-005, TSK-011 | Model + API tests cho cá thể/nhóm |
| FR-PEN-001 | DES-MOD-003, DOMAIN-001 | TSK-005, TSK-012 | Domain relation + API tests |
| FR-CARE-001 | DES-MOD-004, DOMAIN-001 | TSK-006, TSK-013 | Validation + API tests |
| FR-FEED-001 | DES-MOD-004, DOMAIN-001 | TSK-006, TSK-013 | Feed record tests |
| FR-MED-001 | DES-MOD-004, DOMAIN-001 | TSK-006, TSK-013 | Medicine record tests |
| FR-VAX-001 | DES-MOD-005, DOMAIN-001, AI-002 | TSK-007, TSK-014, TSK-021 | Schedule/status + AI reminder tests |
| FR-GROW-001 | DES-MOD-006, DOMAIN-001, UI-002 | TSK-008, TSK-015, TSK-025 | Growth/model/API/UI tests |
| FR-REPRO-001 | DES-MOD-006, DOMAIN-001 | TSK-008, TSK-015 | Reproduction tests |
| FR-ALERT-001 | DES-MOD-005, AI-002, UI-002 | TSK-007, TSK-014, TSK-021, TSK-025 | Due-date + UI alert tests |
| FR-SALE-001 | DES-MOD-007, DOMAIN-001, API-008 | TSK-009, TSK-016 | Sale CRUD tests |
| FR-REV-001 | DES-MOD-007, API-008 | TSK-009, TSK-016 | Revenue consistency tests |
| FR-STAT-001 | DES-MOD-008, API-009, UI-001 | TSK-017, TSK-025 | Aggregate/API/dashboard tests |
| FR-STAT-002 | DES-MOD-008, DOMAIN-001, DOMAIN-002, DOMAIN-004, API-009, UI-001 | TSK-017, TSK-025 | `CostRecord` persistence/validation, cost aggregation/category/date-range tests |
| FR-STAT-003 | DES-MOD-008, DOMAIN-001, DOMAIN-002, DOMAIN-004, API-009, UI-001 | TSK-017, TSK-025 | `HerdLossRecord` persistence/validation, loss formula/reporting-period tests |
| FR-AI-001 | DES-MOD-009, AI-001, AI-002, API-010 | TSK-020, TSK-021, TSK-024 | Mock provider + manual AI scenario |
| FR-AI-002 | DES-MOD-009, AI-001, AI-003, API-010 | TSK-020, TSK-022, TSK-024 | Input mapping + output validation |
| FR-AI-003 | DES-MOD-009, AI-001, AI-004, API-010 | TSK-020, TSK-023, TSK-024 | Growth input/output tests |
| FR-AI-004 | DES-MOD-009, AI-001, SEC-006 | TSK-019, TSK-020 | Data-scope tests |
| FR-AI-005 | AI-005, UI-003 | TSK-024, TSK-025 | Safety notice/UI tests |
| NFR-SEC-001 | SEC-002, SEC-002a, PD-ROLE-001 | TSK-004, TSK-019 | Permission/security regression theo matrix đã phê duyệt |
| NFR-SEC-002 | SEC-005 | TSK-002, TSK-019 | Secret scan/config test |
| NFR-SEC-003 | SEC-006 | TSK-019, TSK-020 | Data-scope AI tests |
| NFR-REL-001 | DES-MOD-002..008, DOMAIN-004 | TSK-005..TSK-017 | Persistence/invariant regression |
| NFR-REL-002 | ERR-001, ERR-002 | TSK-018, TSK-028 | Error-path + regression tests |
| NFR-USAB-001 | UI-002, UI-003 | TSK-024, TSK-025, TSK-026 | UI smoke/accessibility checks |
| NFR-TECH-001 | TD-001..TD-005 | TSK-001, TSK-002, TSK-003, TSK-026, TSK-030 | Environment/build/run verification |
| PD-SEED-001 | PD-SEED-001 | TSK-027 | Management-command, exact reserved-count, DEBUG gate, idempotence, non-demo preservation, statistics and AI factual-source tests |

## Coverage Check

### MUST requirements

Tất cả MUST requirements trong `docs/01_requirements.md` đều có ít nhất một Implementation Task trong traceability. Không có MUST requirement bị bỏ trống:

```text
FR-AUTH-001, FR-AUTH-002,
FR-HERD-001, FR-HERD-002, FR-PEN-001,
FR-CARE-001, FR-FEED-001, FR-MED-001, FR-VAX-001,
FR-GROW-001, FR-ALERT-001, FR-SALE-001, FR-REV-001,
FR-STAT-001, FR-STAT-002, FR-STAT-003,
FR-AI-001, FR-AI-002, FR-AI-003, FR-AI-004, FR-AI-005,
NFR-SEC-001, NFR-SEC-002, NFR-SEC-003,
NFR-REL-001, NFR-REL-002, NFR-TECH-001
```

`FR-REPRO-001` và `NFR-USAB-001` được giữ trong plan dù priority thấp hơn MUST vì đã tồn tại trong Design và phải có task/verification khi còn trong phạm vi triển khai.

### Design coverage

Các nhóm Design quan trọng đã có task tương ứng:

```text
TD-*        -> TSK-001,002,003,026,030
ARCH-*      -> TSK-003,010,025,028,030
DES-MOD-*   -> TSK-004..025
DOMAIN-*    -> TSK-005..010
API-*       -> TSK-011..018,021..023,028
AI-*        -> TSK-020..024
UI-*        -> TSK-025,026
ERR-*       -> TSK-018,028
SEC-*       -> TSK-002,004,019,020,024,029
PD-SEED-001 -> TSK-027
```

## Quality Gate / Validation

`docs/03_implementation_plan.md` chỉ được `STATUS: PASS` khi:

- Mỗi MUST requirement ánh xạ tới ít nhất một Implementation Task.
- Mỗi Design ID quan trọng có task triển khai hoặc verification task.
- Dependency rõ ràng.
- Mỗi task có test hoặc verification command.
- Mỗi task có Definition of Done.
- Không tạo source code trong bước 03.
- Có `Skills.sh Evidence`.
- Nội dung tiếng Việt đúng UTF-8.
- Không có blocker/critical về coverage hoặc dependency.

## Outputs

Tạo hoặc cập nhật:

- `docs/03_implementation_plan.md`

## Acceptance Criteria

- `docs/03_implementation_plan.md` tồn tại.
- Có task list.
- Có dependency matrix.
- Có test plan.
- Có Definition of Done.
- Có backtrack rule.
- Có Requirement -> Design -> Implementation traceability.
- Không tạo source code.
- `NEXT_PROMPT` trỏ đúng `prompts/04_implementation.md`.

## Handoff to Next Stage

Chỉ chuyển sang `prompts/04_implementation.md` khi artifact này có `STATUS: PASS`.

STATUS: PASS
NEXT_INPUT: docs/03_implementation_plan.md
NEXT_PROMPT: prompts/04_implementation.md
TRACEABILITY_MATRIX_UPDATED: YES
