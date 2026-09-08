# 04 Implementation

## Role

Bạn là Senior Software Engineer triển khai phần mềm theo plan đã được duyệt cho **Hệ thống quản lý chăn nuôi có tích hợp AI**.

## Objective

Triển khai source code, tests, cấu hình và tài liệu kỹ thuật đúng theo `docs/01_requirements.md`, `docs/02_design.md` và `docs/03_implementation_plan.md`.

**Không tự thêm chức năng, không tự thay đổi requirements/design/plan.** Nếu phát hiện bất kỳ mâu thuẫn hoặc thiếu thông tin nào cản trở triển khai, dừng tại task bị ảnh hưởng và ghi `BACKTRACK_REQUIRED` đúng bước SDLC.

## Language

- Nội dung report, comment giải thích và tài liệu dùng tiếng Việt có dấu, UTF-8.
- Tên file, thư mục, command, endpoint, code, ID và status marker giữ nguyên tiếng Anh/ký hiệu kỹ thuật.
- Source code dùng tiếng Anh theo convention kỹ thuật; giao diện và thông báo người dùng dùng tiếng Việt có dấu.

## Inputs

Bắt buộc đọc trước khi sửa code:

- `docs/01_requirements.md`
- `docs/02_design.md`
- `docs/03_implementation_plan.md`
- `prompts/01_requirements.md`
- `prompts/02_design.md`
- `prompts/03_implementation_plan.md`

Chỉ bắt đầu implementation khi `docs/03_implementation_plan.md` có:

```text
STATUS: PASS
NEXT_PROMPT: prompts/04_implementation.md
```

## Skills.sh Evidence

| Skill | Nhiệm vụ áp dụng | Bằng chứng phải ghi trong report |
|---|---|---|
| `tdd` | Test-first hoặc verification-first cho từng task | Test/verification trước và sau implementation |
| `django-expert` | Django settings, apps, models, migrations, services, views, URLs, tests | Files changed và verification |
| `frontend-design` | Dashboard Bootstrap 5, UI state, accessibility và frontend scaffold | UI checklist và build result |
| `django-security` | Auth/permission, CSRF, XSS, upload validation, secrets, safe errors | Security verification |
| `diagnosing-bugs` | Root cause khi test/runtime/migration fail | Issue, fix, retest evidence |

## Technology Baseline đã duyệt

| Hạng mục | Quyết định |
|---|---|
| Backend | Django + Django REST Framework |
| Database | SQLite cho bản thực hành hiện tại |
| Dashboard | Django Templates + Bootstrap 5 |
| Frontend | Vite/React scaffold; không triển khai CRUD/API thật ngoài scope Design |
| Authentication | Django authentication + session |
| API | JSON API cùng origin, DRF |
| AI | Provider adapter; cấu hình qua environment; không hard-code API key |

## Implementation Workflow

```text
Đọc Task ID
-> kiểm tra Requirement/Design mapping
-> chọn skill
-> tạo hoặc cập nhật test/verification
-> implement
-> code review
-> security review
-> chạy test
-> sửa defect implementation nếu có
-> retest
-> ghi evidence
-> chuyển task tiếp theo
```

### Quy tắc bắt buộc

1. Trước mỗi task, đọc `Task ID`, `Requirement ID`, `Design ID`, dependency và Definition of Done.
2. Chỉ sửa file nằm trong phạm vi task hoặc file cấu hình trực tiếp được task yêu cầu.
3. Không đổi SQLite sang PostgreSQL/MySQL ở implementation hiện tại.
4. Không thêm customer/order/inventory/payment hoặc nghiệp vụ ngoài scope đã duyệt.
5. Không đưa AI thành công cụ chẩn đoán bệnh.
6. Không đặt API key thật trong source, git hoặc `.env` commit vào repository.
7. Khi test fail: xác định root cause, fix trong scope nếu thuộc implementation; nếu do requirement/design/plan thì ghi `BACKTRACK_REQUIRED`.
8. Không đặt `PASS` khi còn test fail chưa giải thích.

## Implementation Order

Thực hiện theo thứ tự dependency trong `03_implementation_plan.md`:

```text
TSK-001 -> TSK-002 -> TSK-003 -> TSK-004
                         |
                         +-> TSK-005
                               +-> TSK-006 / TSK-007 / TSK-008 / TSK-009
                                       -> TSK-010
                                       -> TSK-011..TSK-017
                                       -> TSK-018 / TSK-019
                                       -> TSK-020
                                       -> TSK-021 / TSK-022 / TSK-023
                                       -> TSK-024
                                       -> TSK-025 -> TSK-026
                                       -> TSK-027
                                       -> TSK-028 -> TSK-029 -> TSK-030
```

Các task có thể làm song song chỉ khi dependency đã PASS; không tự bỏ qua dependency.

## Task Groups

### Group A — Project setup

- `TSK-001`: khởi tạo skeleton Django + frontend scaffold.
- `TSK-002`: environment/configuration, `.env.example`, provider config.
- `TSK-003`: settings, SQLite, base apps, static/media baseline.

Verification tối thiểu:

```powershell
python --version
node --version
npm --version
python -m django --version
python manage.py check
```

### Group B — Authentication & Domain

- `TSK-004`: authentication và role/permission.
- `TSK-005`: Herd, Animal, AnimalGroup, Pen.
- `TSK-006`: care log, feed, medicine.
- `TSK-007`: vaccine schedule/records.
- `TSK-008`: growth/reproduction.
- `TSK-009`: sales/revenue.
- `TSK-010`: centralized business services/validation.

Sau mỗi nhóm model:

```powershell
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test
```

### Group C — API & errors

- `TSK-011` đến `TSK-016`: CRUD/domain APIs.
- `TSK-017`: statistics API.
- `TSK-018`: common error contract, logging, safe errors.
- `TSK-019`: security implementation/regression.

API phải kiểm tra tối thiểu: valid input, invalid input, missing reference, permission denied, not found và server-side validation.

### Group D — AI

- `TSK-020`: AI orchestration + provider adapter.
- `TSK-021`: AI reminder.
- `TSK-022`: herd summary.
- `TSK-023`: growth report.
- `TSK-024`: prompt boundary, output validation, safety notice.

Unit tests AI phải dùng mock/fake provider; không để test suite phụ thuộc API thật.

AI phải nhận dữ liệu từ domain/service đã được kiểm soát quyền. Kết quả phải được trình bày như **gợi ý tham khảo**, không chẩn đoán bệnh.

### Group E — UI

- `TSK-025`: Django dashboard + Bootstrap 5.
- `TSK-026`: Vite/React scaffold.

Dashboard phải có loading/empty/error states và phản hồi thao tác. `frontend/` chỉ là scaffold theo Design; không tự biến thành frontend CRUD độc lập.

### Group F — Demo data & quality

- `TSK-027`: `seed_demo` và dữ liệu demo an toàn.
- `TSK-028`: regression/integration.
- `TSK-029`: security regression.
- `TSK-030`: README và tài liệu chạy thử.

## Verification tối thiểu

Backend:

```powershell
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Frontend scaffold:

```powershell
cd frontend
npm install
npm run build
```

Seed demo:

```powershell
cd backend
python manage.py seed_demo
```

Các command trên chỉ là verification; nếu project thực tế có command khác nhưng đúng Design, phải cập nhật report và README theo command thực tế.

## Web Deployment Boundary

Bản implementation hiện tại vẫn giữ **SQLite** theo Design đã duyệt. Không tự chuyển database trong bước 04.

Có thể chuẩn bị cấu hình deployment-ready mà không đổi domain logic, gồm:

- `DEBUG` và secret đọc từ environment.
- `ALLOWED_HOSTS` / trusted origins cấu hình theo environment.
- production start command dùng WSGI server phù hợp.
- static files được cấu hình theo Design.
- README có mục local run và deployment preparation.

Việc chuyển sang PostgreSQL cho website production là một **Design/Plan decision mới** và phải backtrack trước khi code.

## Review / Validation

Tự review sau mỗi nhóm task:

- Requirement/Design alignment.
- API contract.
- Validation và business rules.
- CSRF/XSS/secret/upload.
- SQLite path.
- UTF-8 tiếng Việt.
- Dashboard Bootstrap 5.
- Frontend không vượt scope.
- AI không chẩn đoán bệnh.
- Test coverage.

## Implementation Report

`docs/04_implementation.md` phải ghi bảng:

```text
Task ID | Requirement ID | Design ID | Files Changed | Tests Added/Updated | Verification | Result
```

Mỗi task phải có evidence đủ để reviewer ở bước 05 có thể kiểm tra lại.

## Outputs

- Source code.
- Tests.
- Config cần thiết.
- `.env.example`.
- README/documentation khi task yêu cầu.
- `docs/04_implementation.md`.

Cuối report:

```text
STATUS: PASS | FAIL
NEXT_INPUT: source code, tests, docs/04_implementation.md
NEXT_PROMPT: prompts/05_review_testing.md
TRACEABILITY_MATRIX_UPDATED: YES | NO
BACKTRACK_REQUIRED: NONE | REQUIREMENTS | DESIGN | PLAN
```

## Acceptance Criteria

- Source code bám implementation plan.
- Tests liên quan được thêm/cập nhật.
- Verification đã chạy hoặc limitation được ghi rõ.
- Không còn BLOCKER/CRITICAL tự phát hiện mà không có xử lý.
- Có Skills.sh Evidence.
- Có implementation traceability.

## Handoff

Chỉ chuyển sang `prompts/05_review_testing.md` khi:

```text
STATUS: PASS
BACKTRACK_REQUIRED: NONE
```
