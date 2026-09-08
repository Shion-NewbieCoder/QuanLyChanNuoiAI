# 02 Design

## Role

Bạn là Kiến trúc sư phần mềm, Django Engineer và UI/UX Designer.

## Objective

Xác định phần mềm sẽ được thiết kế như thế nào dựa trên `docs/01_requirements.md` đã được review và chấp thuận cho đề tài **Hệ thống quản lý chăn nuôi có tích hợp AI**.

Tài liệu này thiết kế kiến trúc tổng thể, module backend, logical domain model, API contract, dashboard/UI-UX, AI integration, validation/error handling và security controls. Tài liệu không viết source code và không lặp lại toàn bộ requirements.

## Inputs

- `docs/01_requirements.md`.
- `prompts/01_requirements.md` và cấu trúc file mẫu do giảng viên cung cấp.
- Project Brief chính thức: **Hệ thống quản lý chăn nuôi có tích hợp AI**.

## Requirement Gate

Đầu vào đáp ứng điều kiện chuyển sang Design:

```text
STATUS: PASS
NEXT_PROMPT: prompts/02_design.md
```

## Skills.sh Evidence

| Skill | Nhiệm vụ áp dụng | Đầu ra đã dùng | Vị trí bằng chứng |
|---|---|---|---|
| `codebase-design` | Xác định module, interface và seam giữa dashboard, backend, API và AI adapter; ưu tiên thiết kế có thể kiểm thử qua interface nhỏ | Module boundary, contract và seam cho domain, API và AI provider | `Architecture`, `Backend Module Design`, `AI Design` |
| `django-expert` | Chọn cách tổ chức Django app, ORM, authentication, permissions, views và tests theo convention | Backend Django, app boundaries, authentication và API layer | `Technology Decision`, `Backend Module Design` |
| `domain-modeling` | Chuẩn hóa entity, trạng thái và luật nghiệp vụ của miền chăn nuôi | Logical model cho đàn, cá thể/nhóm, chuồng, chăm sóc, vaccine, tăng trưởng, sinh sản, xuất bán | `Logical Domain Model` |
| `frontend-design` | Thiết kế dashboard, layout, trạng thái, accessibility và thông báo lỗi | Dashboard Bootstrap 5, các màn hình nghiệp vụ và trạng thái UI | `Dashboard / UI-UX Design` |
| `django-security` | Thiết kế authentication, authorization, CSRF, XSS, upload validation, secret handling và safe error | Security controls và error handling | `Security Design`, `Validation & Error Handling` |

Các skill được sử dụng đúng theo mục đích mà template Design yêu cầu: thiết kế ranh giới module và interface, thiết kế Django backend, mô hình miền dữ liệu, UI/UX và các kiểm soát bảo mật.

## Technology Decision

### TD-001 — Backend: Django + Django REST Framework

**Quyết định thiết kế:** Chọn Django làm backend và Django REST Framework (DRF) làm lớp API.

**Lý do:**
- Phù hợp trực tiếp với template Design của giảng viên, trong đó role và scope được thiết kế theo Django.
- Django cung cấp authentication, permissions, ORM, migrations và admin phù hợp với hệ thống nhiều nhóm nghiệp vụ.
- DRF phù hợp để tách API JSON cho dashboard và các chức năng AI.

**Quan hệ với OQ-001:** OQ-001 của Requirements được giải quyết ở giai đoạn Design bằng quyết định TD-001.

### TD-002 — Database: SQLite cho bản chạy thực hành

**Quyết định thiết kế:** Dùng SQLite cho phiên bản thực hành/demo ban đầu.

**Lý do:**
- Project Brief cho phép SQLite.
- Dễ chạy cục bộ trên VS Code, không yêu cầu cài thêm database server.
- Phù hợp giai đoạn bài tập hiện tại.

Khả năng thay thế bằng MySQL/PostgreSQL được giữ ở mức migration-compatible trong thiết kế ORM, không thay đổi domain model.

### TD-003 — Dashboard: Django Templates + Bootstrap 5

**Quyết định thiết kế:** Dashboard chính được Django render bằng template và Bootstrap 5.

**Lý do:**
- Giảm độ phức tạp triển khai cho bài tập hiện tại.
- Cùng một backend có thể render trang quản trị và cung cấp JSON API.
- Bootstrap đáp ứng bảng dữ liệu, form, modal, alert, card thống kê và responsive layout.

### TD-004 — Frontend scaffold: Vite/React ở mức scaffold

`frontend/` được giữ như scaffold Vite/React tương tự cấu trúc mẫu, nhưng không phải giao diện CRUD chính trong phiên bản bài tập hiện tại. CRUD thực tế dùng Django Templates + Bootstrap.

### TD-005 — AI provider: Adapter-based, provider configurable

Không chốt cứng OpenAI/Gemini/Claude/Hugging Face/Ollama ở Design vì Project Brief cho phép nhiều lựa chọn. Hệ thống thiết kế một `AI Provider Interface` và một adapter cụ thể ở Implementation. Provider cụ thể sẽ được ghi nhận trong `03_implementation_plan.md` hoặc quyết định implementation tương ứng.

Lợi ích: không để nghiệp vụ chăn nuôi phụ thuộc trực tiếp vào một SDK/model cụ thể; có thể thay provider mà không thay đổi use case AI.

---

## Architecture

### ARCH-001 — Kiến trúc tổng thể

```text
                    +------------------------------+
                    |      User / Web Browser       |
                    +---------------+--------------+
                                    |
                                    v
                    +------------------------------+
                    | Django Templates + Bootstrap 5|
                    | Dashboard / Forms / Reports   |
                    +---------------+--------------+
                                    |
                                    v
                    +------------------------------+
                    | Django Application            |
                    | Auth / Views / Domain Services|
                    +---------------+--------------+
                                    |
                 +------------------+------------------+
                 |                  |                  |
                 v                  v                  v
        +----------------+  +---------------+  +------------------+
        | Django ORM     |  | DRF API       |  | AI Orchestrator  |
        | Domain Models  |  | JSON Contract |  | + Provider Adapter|
        +-------+--------+  +---------------+  +---------+--------+
                |                                      |
                v                                      v
        +----------------+                     +------------------+
        | SQLite         |                     | AI Provider      |
        | database       |                     | configurable     |
        +----------------+                     +------------------+
```

### ARCH-002 — Luồng dữ liệu nghiệp vụ

```text
User
  -> Dashboard
  -> Django View / DRF Endpoint
  -> Validation + Permission
  -> Domain Service
  -> ORM
  -> SQLite
  -> JSON / HTML response
```

### ARCH-003 — Luồng AI

```text
User
  -> AI feature
  -> Permission check
  -> Data selection from DB
  -> Data minimization / formatting
  -> Prompt Builder
  -> AI Orchestrator
  -> AI Provider Adapter
  -> AI Provider
  -> Response validation
  -> UI + safety notice
```

AI không truy cập database trực tiếp. AI chỉ nhận dữ liệu do application layer chọn và kiểm soát.

## Module Boundaries

| Design ID | Module | Trách nhiệm | Interface chính |
|---|---|---|---|
| DES-MOD-001 | Authentication & Authorization | Đăng nhập, session, role và permission | Django auth / permission checks |
| DES-MOD-002 | Herd Management | Quản lý đàn, cá thể và nhóm | Domain services + `/api/herds` |
| DES-MOD-003 | Pen Management | Quản lý chuồng và liên kết đàn | Domain services + `/api/pens` |
| DES-MOD-004 | Care Management | Nhật ký chăm sóc, thức ăn, thuốc | Domain services + `/api/care-logs` |
| DES-MOD-005 | Vaccination Management | Lịch vaccine, bản ghi tiêm và lịch cần nhắc | Domain services + `/api/vaccinations` |
| DES-MOD-006 | Growth & Reproduction | Cân nặng, tăng trưởng, sinh sản | Domain services + `/api/growth-records`, `/api/reproduction-records` |
| DES-MOD-007 | Sales Management | Xuất bán và doanh thu | Domain services + `/api/sales` |
| DES-MOD-008 | Statistics | Tổng hợp tăng trưởng; chi phí từ `CostRecord`; hao hụt từ `HerdLossRecord` | Query/report services |
| DES-MOD-009 | AI Orchestrator | Chuẩn hóa input/output, gọi adapter, xử lý lỗi | `AIProviderInterface` |
| DES-MOD-010 | Dashboard | Hiển thị số liệu và kết quả nghiệp vụ/AI | Django Templates |

## Logical Domain Model

### DOMAIN-001 — Các thực thể logic

| Entity | Mục đích | Thuộc tính logic chính |
|---|---|---|
| User | Tài khoản và vai trò | id, username, password credential, role, status |
| Herd | Đàn vật nuôi | id, code/name, animal type, management mode, quantity/status |
| Animal | Cá thể vật nuôi | id, code, herd, basic attributes, status |
| AnimalGroup | Nhóm vật nuôi | id, code/name, herd, quantity, status |
| Pen | Chuồng trại | id, code/name, location/description, status |
| CareLog | Nhật ký chăm sóc | id, target -> Herd, date/time, activity, notes |
| FeedRecord | Ghi nhận thức ăn | id, target, date/time, feed type, quantity, notes |
| MedicineRecord | Ghi nhận thuốc | id, target, date/time, medicine, quantity/dose, notes |
| VaccineSchedule | Lịch vaccine | id, target, vaccine, scheduled date, status |
| VaccinationRecord | Kết quả tiêm vaccine | id, schedule, actual date, notes |
| GrowthRecord | Số liệu tăng trưởng | id, target, measurement date, weight, notes |
| ReproductionRecord | Sự kiện sinh sản | id, target -> Herd, event_date, event_type (text, required), result (optional), notes (optional) |
| SaleRecord | Xuất bán | id, target -> Herd, sale_date, quantity (optional), weight (optional), amount (required), notes (optional) |
| HerdLossRecord | Dữ liệu nguồn hao hụt theo kỳ báo cáo | id, herd -> Herd, period_start, period_end, opening_quantity, lost_quantity, notes (optional) |
| CostRecord | Dữ liệu nguồn chi phí | id, herd -> Herd, cost_date, category, amount, notes (optional) |
| AIRequest | Dấu vết yêu cầu AI ở mức ứng dụng | id, feature type, requested by, created time, input summary/status |
| AIResponse | Kết quả AI đã kiểm tra | id, request, provider marker, response status, validated result |

### DOMAIN-002 — Quan hệ logic

```text
User
  1 ------ * AIRequest

Herd
  1 ------ * Animal
  1 ------ * AnimalGroup
  1 ------ * CareLog
  1 ------ * FeedRecord
  1 ------ * MedicineRecord
  1 ------ * VaccineSchedule
  1 ------ * GrowthRecord
  1 ------ * ReproductionRecord
  1 ------ * SaleRecord
  1 ------ * HerdLossRecord
  1 ------ * CostRecord

Pen
  1 ------ * Herd / AnimalGroup / Animal (tùy mức quản lý được chọn)

VaccineSchedule
  1 ------ 0..* VaccinationRecord

AIRequest
  1 ------ 0..1 AIResponse
```

- `CareLog.target`: bắt buộc, tham chiếu `Herd` trong phạm vi triển khai ban đầu; đây là quyết định thiết kế của dự án để giải quyết sự mơ hồ trong nguồn gốc đề bài. `Animal` và `AnimalGroup` không phải target của `CareLog` trong phạm vi ban đầu.
- `ReproductionRecord.target`: bắt buộc, tham chiếu `Herd`; triển khai ban đầu không tích hợp mục tiêu sinh sản ở mức `Animal` hoặc `AnimalGroup`.
- `ReproductionRecord.event_date`: bắt buộc.
- `ReproductionRecord.event_type`: bắt buộc, lưu dưới dạng text đơn giản; không định nghĩa enum mới cho các sự kiện sinh sản.
- `ReproductionRecord.result`: tùy chọn.
- `ReproductionRecord.notes`: tùy chọn.
- `SaleRecord.target`: bắt buộc, tham chiếu `Herd`; triển khai ban đầu không tích hợp mục tiêu xuất bán ở mức `Animal` hoặc `AnimalGroup`.
- `SaleRecord.sale_date`: bắt buộc.
- `SaleRecord.quantity`: tùy chọn; hỗ trợ lưu số lượng khi có dữ liệu phù hợp, nhưng không bắt buộc cho mọi bản ghi xuất bán.
- `SaleRecord.weight`: tùy chọn; hỗ trợ lưu khối lượng khi có dữ liệu phù hợp, nhưng không bắt buộc cho mọi bản ghi xuất bán.
- `SaleRecord.amount`: bắt buộc; lưu tổng giá trị tiền mặt của bản ghi xuất bán đó.
- `SaleRecord.notes`: tùy chọn.
- `SaleRecord.amount` là căn cứ cho báo cáo doanh thu trong phạm vi ban đầu; không tạo model doanh thu riêng biệt (`RevenueRecord`).
- Không thêm `unit_price` hoặc `currency` cho `SaleRecord` trong triển khai ban đầu trừ khi có nguồn hiện tại khác yêu cầu rõ ràng.
- Không tạo mục tiêu xuất bán đa hình; `SaleRecord` chỉ tham chiếu `Herd` trong phạm vi ban đầu.
- `HerdLossRecord` là dữ liệu nguồn đã được Project Design Decision phê duyệt cho tỷ lệ hao hụt; không suy diễn hao hụt từ sale, thay đổi số lượng hiện tại, sinh sản hoặc chênh lệch số lượng tùy ý.
- `CostRecord` là dữ liệu nguồn đã được Project Design Decision phê duyệt cho thống kê chi phí; không suy diễn chi phí từ quantity/dose hoặc vaccine record khi không có `CostRecord` rõ ràng.

### DOMAIN-003 — Nguyên tắc trạng thái

- Status là bắt buộc chỉ với entity có lifecycle/workflow và ngữ nghĩa status được Design xác định rõ. Không đặt một danh sách status duy nhất cho mọi entity; status phải thuộc đúng ngữ cảnh nghiệp vụ.
- Các factual business log/record không bắt buộc có status khi DOMAIN-001 và Requirements liên kết không xác định thuộc tính status, lifecycle hoặc hành vi status.
- Lịch vaccine có persisted lifecycle status cố định: `scheduled`, `due`, `completed`, `cancelled`.
  - `scheduled`: lịch đã được lập nhưng chưa ở trạng thái due.
  - `due`: lịch đến hạn / cần chú ý theo lifecycle state của `VaccineSchedule`.
  - `completed`: lịch đã được thực hiện.
  - `cancelled`: lịch đã bị hủy / bỏ qua.
- Không thêm persisted status khác cho `VaccineSchedule.status`.
- Các phân loại cảnh báo dẫn xuất theo OQ-005 (`overdue`, `due today`, `due soon`, `scheduled / not-yet-due`) là derived alert classification và không được lưu vào `VaccineSchedule.status`.
- `cancelled` là trạng thái persisted cho lịch đã hủy/bỏ qua; không tạo status `skipped` riêng nếu không có xác nhận nghiệp vụ riêng biệt.
- AI response có trạng thái xử lý riêng: pending, success, failed hoặc invalidated ở mức kỹ thuật.

### DOMAIN-004 — Business invariant cần được bảo vệ

1. Mọi bản ghi nghiệp vụ phải tham chiếu một đối tượng hợp lệ.
2. Dữ liệu tăng trưởng phải có measurement date và weight hợp lệ.
3. Vaccine schedule phải xác định được target và scheduled date.
4. `SaleRecord.target` phải tham chiếu một `Herd` hợp lệ; `SaleRecord.amount` phải là số tiền hợp lệ và không âm; `quantity`/`weight` nếu có thì phải là giá trị hợp lệ và không âm.
5. Doanh thu được báo cáo từ `SaleRecord.amount`; không tạo `RevenueRecord` riêng trong phạm vi triển khai ban đầu.
6. AI không được coi là nguồn dữ liệu gốc; database nghiệp vụ mới là source of truth.
7. `HerdLossRecord.herd` phải hợp lệ; `opening_quantity > 0`, `lost_quantity >= 0`, `lost_quantity <= opening_quantity` và `period_end >= period_start`.
8. `CostRecord.herd` phải hợp lệ; `cost_date`, `category`, `amount` là bắt buộc và `amount >= 0`. Category ban đầu chỉ là `feed`, `medicine`, `vaccine`, `care`, `other`.
9. `loss_rate_percent = SUM(lost_quantity) / SUM(opening_quantity) * 100`, chỉ từ `HerdLossRecord` đủ điều kiện. Khi có `start_date`/`end_date`, chỉ tổng hợp các kỳ nằm trong khoảng; không có khoảng thì tổng hợp toàn bộ.
10. `total_cost = SUM(CostRecord.amount)`; có thể nhóm theo category. Lọc ngày tùy chọn dùng `CostRecord.cost_date`; không có khoảng thì tổng hợp toàn bộ.

## API Contract

Thiết kế API ở mức contract, chưa phải source code.

### API-001 — Health

`GET /health/`

Response success conceptually:

```text
status = "ok"
```

Mục đích: kiểm tra ứng dụng đang hoạt động.

### API-002 — Authentication Context

Session authentication được dùng cho dashboard Django. Các endpoint nghiệp vụ phải kiểm tra authenticated user và role trước khi trả dữ liệu hoặc xử lý action. Authorization dùng matrix `PD-ROLE-001`; action không được cấp phải trả `403`.

### API-003 — Herds

```text
GET    /api/herds
POST   /api/herds
GET    /api/herds/{id}
PATCH  /api/herds/{id}
DELETE /api/herds/{id}
```

Dữ liệu request/response ở mức logical gồm mã/tên đàn, loại vật nuôi, phương thức quản lý, số lượng và trạng thái.

### API-004 — Pens

```text
GET    /api/pens
POST   /api/pens
GET    /api/pens/{id}
PATCH  /api/pens/{id}
DELETE /api/pens/{id}
```

### API-005 — Care / Feed / Medicine

```text
GET  /api/care-logs
POST /api/care-logs
GET  /api/feed-records
POST /api/feed-records
GET  /api/medicine-records
POST /api/medicine-records
```

### API-006 — Vaccination

```text
GET  /api/vaccinations
POST /api/vaccinations
GET  /api/vaccinations/{id}
PATCH /api/vaccinations/{id}
```

### API-007 — Growth & Reproduction

```text
GET  /api/growth-records
POST /api/growth-records
GET  /api/reproduction-records
POST /api/reproduction-records
```

### API-008 — Sales

```text
GET  /api/sales
POST /api/sales
GET  /api/sales/{id}
PATCH /api/sales/{id}
```

### API-009 — Statistics

```text
GET /api/statistics/growth
GET /api/statistics/costs
GET /api/statistics/mortality
```

Các endpoint thống kê là read-only ở tầng API.

- `/api/statistics/costs` tổng hợp `CostRecord.amount` và có thể nhóm theo category; nhận `start_date`/`end_date` tùy chọn theo `cost_date`.
- `/api/statistics/mortality` tính `loss_rate_percent` từ `HerdLossRecord`; nhận `start_date`/`end_date` tùy chọn và chỉ dùng các kỳ nằm trong khoảng báo cáo.

### API-010 — AI Features

```text
POST /api/ai/reminders
POST /api/ai/herd-summary
POST /api/ai/growth-report
```

`POST /api/ai/herd-summary` nhận `{herd_id}` bắt buộc, Herd phải tồn tại; không date filters. Dữ liệu tối thiểu: Herd `id`, `code`, `name`, `animal_type`, `management_mode`, `quantity`, `status`; CareLog `recorded_at`, `activity`, `notes`; FeedRecord `recorded_at`, `feed_type`, `quantity`, `notes`; MedicineRecord `recorded_at`, `medicine`, `dose`, `notes`; VaccineSchedule `vaccine`, `scheduled_date`, `status`; VaccinationRecord `actual_date`, `notes`. Chỉ chọn toàn bộ records approved của Herd, không truncate. Exclude GrowthRecord (TSK-023), reproduction, sale, cost, loss, statistics, AI reminder output and user/auth/group data. Empty related lists vẫn gọi provider với Herd facts, `source_count=0` không tính Herd. Response transient `{status: "success", feature: "herd_summary", result: {text, source_count}, notice: "AI-generated summary based on recorded herd data."}`; không persist hoặc mutate business data.

`POST /api/ai/growth-report` nhận `{herd_id, start_date?, end_date?}`; Herd bắt buộc tồn tại, ngày ISO tùy chọn độc lập và `start_date <= end_date`. Lọc inclusive trên `GrowthRecord.measurement_date`, không implicit cutoff. Adapter chỉ nhận Herd `id`, `code`, `name`; GrowthRecord `measurement_date`, `weight`, `notes`; cùng metrics do application tính: record count, first/last date và weight, absolute/percent change, average weight. Percent change null khi first weight bằng 0. Với dưới 2 records: HTTP 200, không gọi provider, text rỗng, source_count 0/1, metrics khả dụng, change null và notice insufficient-data. Với từ 2 records: response transient `{status: "success", feature: "growth_report", result: {text, source_count, metrics}, notice: "AI-generated growth report based on recorded growth data."}`. Không prediction, persistence hoặc mutation; quyền theo PD-ROLE-001.

`POST /api/ai/reminders` request:

```text
scope: required, all | herd
target_id: required Herd id when scope=herd; null/omitted when scope=all
start_date, end_date: optional ISO dates; start_date <= end_date when both supplied
```

Response:

```text
{status: "success", feature: "reminders", result: {text, source_count}, notice}
```

Với empty qualifying source: HTTP 200, `text` rỗng, `source_count: 0`, notice `No qualifying reminder data.`, và không gọi provider.

`notice` phải chứa cảnh báo rằng AI chỉ cung cấp gợi ý tham khảo và không thay thế bác sĩ thú y/kỹ sư chăn nuôi.

TSK-021 chỉ chọn `VaccineSchedule`, lọc inclusive theo `scheduled_date`, exclude `completed`/`cancelled`, và gửi tối thiểu target identifier, vaccine, scheduled date, persisted status, derived alert classification. Không dùng factual care records như care schedule, không tạo `CareSchedule`, không persist AI request/response/output, và AI không thay đổi business data.

### API-011 — Error Contract

Mọi API lỗi phải trả response có cấu trúc nhất quán ở mức logical:

```text
error_code
message
field_errors (optional)
```

Không trả stack trace hoặc secret cho client.

## AI Design

### AI-001 — AI Orchestrator

`AI Orchestrator` là seam giữa domain application và provider. Nghiệp vụ chỉ gọi orchestrator; không gọi SDK/provider trực tiếp.

### AI-002 — Feature: AI nhắc lịch

**Input:** lịch chăm sóc, lịch vaccine và metadata tối thiểu cần thiết của đối tượng.

**Output:** danh sách lịch cần lưu ý, lý do dựa trên dữ liệu, mức độ ưu tiên tham khảo.

**Ràng buộc:** không tự thêm lịch không có trong dữ liệu nguồn; không chẩn đoán bệnh.

### AI-003 — Feature: Tóm tắt tình trạng đàn

**Input:** nhật ký chăm sóc và số liệu liên quan được người dùng hiện tại được phép xem.

**Output:** tóm tắt diễn biến, điểm nổi bật, dữ liệu thiếu hoặc điểm cần theo dõi.

**Ràng buộc:** không biến mô tả thành chẩn đoán.

### AI-004 — Feature: Báo cáo tăng trưởng

**Input:** lịch sử cân nặng/tăng trưởng trong khoảng thời gian được chọn.

**Output:** xu hướng, thay đổi đáng chú ý, điểm cần theo dõi.

**Ràng buộc:** nếu dữ liệu quá ít hoặc không liên tục, phải nói rõ hạn chế.

### AI-005 — Prompt boundary

System prompt logic:

```text
Bạn là trợ lý quản lý chăn nuôi.
Chỉ đưa gợi ý tham khảo dựa trên dữ liệu được cung cấp.
Không chẩn đoán bệnh và không thay thế bác sĩ thú y/kỹ sư chăn nuôi.
Không tự bịa dữ liệu không có trong đầu vào.
Nếu dữ liệu không đủ, phải nói rõ dữ liệu chưa đủ.
```

User prompt được tạo từ dữ liệu hệ thống, không lấy trực tiếp raw input không kiểm soát từ trình duyệt.

### AI-006 — Output validation

Trước khi hiển thị:

1. Kiểm tra response có nội dung.
2. Kiểm tra trạng thái provider.
3. Kiểm tra cấu trúc kết quả tối thiểu.
4. Chuẩn hóa text.
5. Gắn safety notice.

Nếu không đạt: trả lỗi nghiệp vụ/technical phù hợp, không coi output lỗi là kết quả hợp lệ.

## Dashboard / UI-UX Design

### UI-001 — Main layout

```text
+------------------------------------------------------+
| Header: Tên hệ thống | Người dùng | Đăng xuất       |
+----------------+-------------------------------------+
| Sidebar        | Dashboard                           |
| - Tổng quan    | KPI cards                           |
| - Đàn          | - Tổng đàn                         |
| - Chuồng       | - Lịch sắp đến                     |
| - Chăm sóc     | - Tăng trưởng                      |
| - Vaccine      | - Doanh thu                        |
| - Tăng trưởng  | Charts / tables / alerts            |
| - Sinh sản     |                                     |
| - Xuất bán     | AI Assistant cards                 |
| - Thống kê     |                                     |
| - AI Assistant |                                     |
+----------------+-------------------------------------+
```

### UI-002 — Các màn hình chính

| Màn hình | Nội dung | Trạng thái bắt buộc |
|---|---|---|
| Dashboard | KPI, lịch cần chú ý, tăng trưởng, doanh thu | loading, empty, success, error |
| Danh sách đàn | Tìm kiếm, lọc, thêm, sửa, xem | loading, empty, validation error |
| Chi tiết đàn | Thông tin đàn + lịch sử | success, not found |
| Chuồng | Danh sách chuồng và đàn liên quan | empty, error |
| Chăm sóc | Nhật ký chăm sóc/thức ăn/thuốc | empty, validation error |
| Vaccine | Lịch vaccine + trạng thái | upcoming, due, completed, error |
| Tăng trưởng | Bảng/biểu đồ cân nặng | insufficient data, success |
| Sinh sản | Sự kiện sinh sản | empty, success |
| Xuất bán | Bản ghi bán + doanh thu | validation error, success |
| AI Assistant | Nhắc lịch, tóm tắt, báo cáo | loading, success, AI error, insufficient data |

### UI-003 — Accessibility và feedback

- Form có label rõ ràng, không chỉ dựa vào placeholder.
- Lỗi validation hiển thị gần trường gây lỗi.
- Hành động lưu/xóa có phản hồi rõ.
- Bảng dữ liệu có empty state khi không có dữ liệu.
- Không dùng màu sắc là tín hiệu duy nhất cho trạng thái.
- Kết quả AI phải được nhận diện là “Gợi ý từ AI”.

## Validation & Error Handling

### ERR-001 — Validation pipeline

```text
Request
  -> Authentication
  -> Authorization
  -> Request validation
  -> Domain validation
  -> Persistence
  -> Response
```

### ERR-002 — Các nhóm lỗi

| Nhóm | Ví dụ | Response |
|---|---|---|
| Authentication | Chưa đăng nhập | 401 / redirect login tùy context |
| Authorization | Không có quyền | 403 |
| Validation | Thiếu hoặc sai dữ liệu | 400 + field errors |
| Not Found | ID không tồn tại | 404 |
| Conflict | Dữ liệu trạng thái không phù hợp | 409 khi cần |
| Internal | Lỗi ngoài dự kiến | 500 + safe message |
| AI Provider | timeout/rate limit/provider error | mã lỗi nghiệp vụ riêng + safe message |

### ERR-003 — Logging

Log tối thiểu:
- timestamp
- module
- request correlation id nếu triển khai
- user id/role ở mức không lộ dữ liệu nhạy cảm
- error code
- exception category

Không log password, API key hoặc toàn bộ dữ liệu nhạy cảm gửi AI.

## Security Design

| Design ID | Control | Mô tả |
|---|---|---|
| SEC-001 | Authentication | Dùng Django authentication; session được bảo vệ. |
| SEC-002 | Authorization | Permission theo effective role trước khi xử lý endpoint/domain operation, theo matrix và precedence `PD-ROLE-001`. |
| SEC-003 | CSRF | Django CSRF protection cho các form/session write operation. |
| SEC-004 | XSS | Escape output server-rendered; không render raw AI HTML không kiểm soát. |
| SEC-005 | AI Secret Handling | API key/provider secret lấy từ environment/configuration, không hard-code. |
| SEC-006 | Data Scope | Chỉ gửi AI dữ liệu người dùng hiện tại được phép xem. |
| SEC-007 | Upload/Import Boundary | Nếu có upload dữ liệu về sau, phải validate loại/kích thước ở server; không coi client validation là đủ. |
| SEC-008 | Safe Errors | Không trả stack trace hoặc secret trong response production/demo. |

### SEC-002a — Reusable Role Permission Semantics

`PD-ROLE-001` là Project Design Decision đã được phê duyệt, không phải matrix được Project Brief gốc xác định. Mọi API nghiệp vụ hiện có áp dụng matrix sau; `delete` chỉ dành cho quản lý.

| Resource / function | Quản lý | Kỹ thuật viên | Nhân viên |
|---|---|---|---|
| Herd, Animal, AnimalGroup, Pen | create, read, update, delete | read | read |
| CareLog, FeedRecord, MedicineRecord | create, read, update, delete | create, read, update | create, read |
| VaccineSchedule, VaccinationRecord | create, read, update, delete | create, read, update | read |
| GrowthRecord, ReproductionRecord | create, read, update, delete | create, read, update | read |
| SaleRecord | create, read, update, delete | read | read |
| Statistics | read/access | read/access | denied |
| AI functions (TSK-020+) | allowed | allowed | denied |

Trong scope ban đầu không có per-user ownership hoặc tenant partitioning. Role được phép đọc một resource type có thể đọc toàn bộ record của type đó; không lọc theo creator và không thêm farm/tenant/team ownership. SEC-006 tiếp tục giới hạn dữ liệu gửi AI theo quyền này và theo AI Design; không tạo AI implementation tại TSK-019.

Effective role phải được resolve tường minh theo thứ tự `quản lý` > `kỹ thuật viên` > `nhân viên`. Khi user thuộc nhiều recognized role, chỉ role ưu tiên cao nhất được dùng để authorization; không union hoặc intersection permissions. User authenticated không có recognized role bị từ chối protected business APIs, statistics và future AI access. Implementation không được dựa vào database row order, Group primary key, alphabetical order hoặc queryset `.first()` không có priority tường minh. Permission denial dùng error contract an toàn hiện có.

## Project Structure Design

```text
project/
  backend/
    manage.py
    requirements.txt
    .env.example
    config/
      __init__.py
      settings.py
      urls.py
      asgi.py
      wsgi.py
    apps/
      users/
      herds/
      pens/
      care/
      vaccinations/
      growth/
      reproduction/
      sales/
      statistics/
      ai_assistant/
    templates/
    static/
    media/
    tests/
  frontend/
    package.json
    vite.config.js
    src/
      components/
      layouts/
      pages/
      services/
      hooks/
      utils/
      routes/
  docs/
    01_requirements.md
    02_design.md
  .gitignore
  README.md
```

Đây là cấu trúc logic của Design; tên file chi tiết và cách tách app sẽ được chốt ở `03_implementation_plan.md` trước khi code.

### PD-SEED-001 — Local Deterministic Demo Data Design

> Đây là Project Design Decision đã được phê duyệt; exact demo accounts, credentials, records và counts không phải chi tiết của Project Brief gốc.

- Chỉ có một entry point: `python manage.py seed_demo`. Command phải kiểm tra `settings.DEBUG` trước khi ghi và từ chối bằng safe command error khi `DEBUG=False`.
- Toàn bộ thao tác seed thực hiện trong `transaction.atomic` khi phù hợp, dùng current ORM/model validation và stable identity với `update_or_create` hoặc cơ chế tương đương. Không flush, delete-all, schema change hay xóa/cập nhật non-demo rows.
- Reserved identity namespace gồm Herd `DEMO-HERD-001`, `DEMO-HERD-002`, user `demo_manager`, `demo_technician`, `demo_employee`, và `DEMO-*` code/name hay stable combination từ field hiện có cho những row còn lại. Re-run khôi phục giá trị/role membership intended của reserved rows nhưng không chạm non-demo data.
- Ba user demo active, non-superuser, không có additional business-role Group và lần lượt chỉ thuộc `quản lý`, `kỹ thuật viên`, `nhân viên`. Password chung `DemoOnly-2026!` là public local-demo credential, không được dùng trong production. Không tạo superuser.
- `anchor_date = timezone.localdate()` được tính mỗi lần chạy. Relative dates của reserved rows được cập nhật trên re-run; identity và count không thay đổi.

| Reserved resource | Exact count | Demo design |
|---|---:|---|
| Herd | 2 | `DEMO-HERD-001` là primary source; `DEMO-HERD-002` cho multiple-Herd/filter/isolation. |
| AnimalGroup / Animal | 2 / 2 | Required fields, valid demo Herd references, reserved codes/names; không taxonomy/rule mới. |
| Pen | 3 | Một Herd-only, một AnimalGroup-only, một Animal-only; mỗi row thỏa XOR. |
| CareLog / FeedRecord / MedicineRecord | 2 / 2 / 2 | Factual history, Herd-only, thuộc primary Herd. |
| VaccineSchedule / VaccinationRecord | 4 / 1 | Primary Herd: `anchor-7d`, `anchor`, `anchor+30d` qualifying; `anchor-30d` completed và có vaccination record. Chỉ persisted status taxonomy hiện có. |
| GrowthRecord | 3 | Primary Herd, `anchor-60d`, `anchor-30d`, `anchor`; weights `100`, `112`, `125`. |
| ReproductionRecord | 1 | Primary Herd; required date và free-text `event_type="breeding"`. |
| SaleRecord | 2 | Primary Herd; total amounts `5000000`, `7500000`; revenue derived. |
| HerdLossRecord | 2 | Historical contained periods; `(100,2)` và `(98,1)`; loss rate derived. |
| CostRecord | 5 | Historical dates; one per category: feed `3000000`, medicine `1200000`, vaccine `800000`, care `1000000`, other `500000`; total derived. |
| Demo users | 3 | Exact accounts/roles nêu trên. |

- Seed data phải đủ cho non-empty Dashboard, growth/cost/loss statistics, sales/revenue; reminder có qualifying VaccineSchedule; Herd Summary có đủ approved factual source categories; Growth Report có ba GrowthRecord.
- Không seed precomputed statistics, AI output/request/response/prompt/history/provider data và không gọi provider. Database/application vẫn là source of truth.
- Test phải đếm reserved namespace, không assert total table counts khi có non-demo data; chạy command hai lần phải giữ count, restore intended demo values/roles, refresh relative dates và bảo toàn non-demo rows.

## Design-to-Requirement Traceability

| Requirement ID | Design ID | Design Component | Rationale |
|---|---|---|---|
| FR-AUTH-001 | DES-MOD-001, SEC-001 | Authentication | Cần xác thực người dùng. |
| FR-AUTH-002 | DES-MOD-001, SEC-002, SEC-002a | Authorization | Cần phân quyền 3 vai trò theo matrix đã phê duyệt. |
| FR-HERD-001 | DES-MOD-002, DOMAIN-001 | Herd Management | Bao phủ quản lý đàn. |
| FR-HERD-002 | DES-MOD-002, DOMAIN-001 | Animal/AnimalGroup | Bao phủ quản lý cá thể hoặc nhóm. |
| FR-PEN-001 | DES-MOD-003, DOMAIN-001 | Pen Management | Bao phủ chuồng trại. |
| FR-CARE-001 | DES-MOD-004, DOMAIN-001 | Care Management | Bao phủ lịch và nhật ký chăm sóc. |
| FR-FEED-001 | DES-MOD-004, DOMAIN-001 | FeedRecord | Bao phủ thức ăn. |
| FR-MED-001 | DES-MOD-004, DOMAIN-001 | MedicineRecord | Bao phủ thuốc. |
| FR-VAX-001 | DES-MOD-005, DOMAIN-001, AI-002 | Vaccination | Bao phủ vaccine và lịch nhắc. |
| FR-GROW-001 | DES-MOD-006, DOMAIN-001, UI-002 | Growth | Bao phủ cân nặng/tăng trưởng và hiển thị. |
| FR-REPRO-001 | DES-MOD-006, DOMAIN-001, DOMAIN-002 | Reproduction | Bao phủ sinh sản theo mô hình `Herd`-scoped ban đầu: target `Herd`, `event_date` bắt buộc, `event_type` text bắt buộc, `result` và `notes` tùy chọn. |
| FR-ALERT-001 | DES-MOD-005, AI-002, UI-002 | Alert | Bao phủ cảnh báo lịch. |
| FR-SALE-001 | DES-MOD-007, DOMAIN-001, API-008 | Sales | Bao phủ xuất bán. |
| FR-REV-001 | DES-MOD-007, API-008 | Sales/Revenue | Doanh thu gắn với SaleRecord. |
| FR-STAT-001 | DES-MOD-008, API-009, UI-001 | Growth Statistics | Bao phủ thống kê tăng trưởng. |
| FR-STAT-002 | DES-MOD-008, DOMAIN-001, DOMAIN-002, DOMAIN-004, API-009, UI-001 | Cost Statistics | Bao phủ `CostRecord`, tổng chi phí và nhóm category theo Project Design Decision OQ-008. |
| FR-STAT-003 | DES-MOD-008, DOMAIN-001, DOMAIN-002, DOMAIN-004, API-009, UI-001 | Mortality Statistics | Bao phủ `HerdLossRecord`, công thức và kỳ báo cáo theo Project Design Decision OQ-007. |
| FR-AI-001 | DES-MOD-009, AI-001, AI-002, API-010 | AI Reminder | AI nhắc lịch dựa trên dữ liệu hệ thống. |
| FR-AI-002 | DES-MOD-009, AI-001, AI-003, API-010 | Herd Summary | AI tóm tắt tình trạng đàn. |
| FR-AI-003 | DES-MOD-009, AI-001, AI-004, API-010 | Growth Report | AI sinh báo cáo tăng trưởng. |
| FR-AI-004 | DES-MOD-009, AI-001, SEC-006 | Data Scope | AI dùng dữ liệu hệ thống theo quyền. |
| FR-AI-005 | AI-005, UI-003 | Safety Notice | Hiển thị giới hạn AI. |
| NFR-SEC-001 | SEC-002, SEC-002a | Authorization | Chặn action trái matrix quyền đã phê duyệt. |
| NFR-SEC-002 | SEC-005 | Secret Handling | Bảo vệ API key/secret. |
| NFR-SEC-003 | SEC-006 | Data Scope | Kiểm soát dữ liệu gửi AI. |
| NFR-REL-001 | DES-MOD-002..008, DOMAIN-004 | Persistence/Invariant | Đảm bảo lưu-truy xuất nhất quán. |
| NFR-REL-002 | ERR-001, ERR-002 | Error Handling | Không crash khi input/AI lỗi. |
| NFR-USAB-001 | UI-002, UI-003 | UI clarity | Phân biệt dữ liệu hệ thống và gợi ý AI. |
| NFR-TECH-001 | TD-001..TD-005 | Technology Decisions | Chọn stack trong phạm vi Project Brief. |
| PD-SEED-001 | PD-SEED-001 | Local Demo Dataset | Chốt command, safety gate, reserved identity/counts, relative dates, idempotence và source coverage cho TSK-027. |

## Design Review / Validation

### Kiểm tra quality gate

- Mỗi MUST requirement có ít nhất một Design ID.
- Không có module chính nào không gắn với requirement hoặc constraint.
- Kiến trúc phù hợp với project structure và mục tiêu chạy thực hành trên môi trường local.
- Backend, API, dashboard, frontend scaffold, logical data model, validation, error handling và security đều được bao phủ.
- Không chứa source code hoàn chỉnh.
- AI được thiết kế như một capability gắn với nghiệp vụ, không đứng tách rời khỏi dữ liệu hệ thống.
- Security không có BLOCKER/CRITICAL ở mức design.
- Các OQ về công nghệ được giải quyết bằng quyết định thiết kế TD-001..TD-005 hoặc giữ lại dưới dạng lựa chọn implementation nơi cần.
- Có `Skills.sh Evidence`.
- Nội dung UTF-8 tiếng Việt có dấu.

**Blocking issues:** Không có.

**Quality Gate:** PASS

## Outputs

Tạo hoặc cập nhật:

```text
docs/02_design.md
```

Cuối file:

```text
STATUS: PASS
NEXT_INPUT: docs/02_design.md
NEXT_PROMPT: prompts/03_implementation_plan.md
TRACEABILITY_MATRIX_UPDATED: YES
```

## Acceptance Criteria

- `docs/02_design.md` tồn tại.
- Có architecture, logical domain model, API contract, UI/UX design và security design.
- Có bảng `Requirement ID -> Design ID`.
- Không tạo source code.
- `NEXT_PROMPT` trỏ đúng `prompts/03_implementation_plan.md`.

## Handoff to Next Stage

Chỉ chuyển sang `prompts/03_implementation_plan.md` khi `docs/02_design.md` có `STATUS: PASS`.

NEXT_INPUT: docs/02_design.md
NEXT_PROMPT: prompts/03_implementation_plan.md
TRACEABILITY_MATRIX_UPDATED: YES
