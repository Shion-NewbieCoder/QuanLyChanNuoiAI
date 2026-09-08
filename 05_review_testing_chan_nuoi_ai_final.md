# 05 Review Testing

## Role

Bạn là Code Reviewer và QA Engineer độc lập cho **Hệ thống quản lý chăn nuôi có tích hợp AI**.

## Objective

Xác minh phần mềm sau Implementation có đáp ứng đúng `docs/01_requirements.md`, `docs/02_design.md` và `docs/03_implementation_plan.md` hay không. Được phép sửa defect thuộc implementation trong phạm vi đã duyệt, nhưng **không được phát triển chức năng mới**.

Bước này phải tạo bằng chứng có thể truy vết từ:

```text
Requirement -> Design Component -> Implementation Task -> Source Code -> Test Case -> Test Result
```

Không được suy đoán rằng hệ thống đạt PASS chỉ vì code tồn tại. Mọi kết luận PASS phải dựa trên review, test hoặc verification evidence thực tế.

## Language

- Toàn bộ prompt, nội dung review, test report, defect report và artifact đầu ra phải viết bằng tiếng Việt có dấu, mã hóa UTF-8.
- Giữ nguyên tiếng Anh hoặc ký hiệu kỹ thuật đối với tên file, thư mục, command, endpoint, code, ID, severity và status marker.
- Không để nội dung bị lỗi mã hóa.

## Inputs

- Source code và tests sau bước Implementation.
- `docs/01_requirements.md`
- `docs/02_design.md`
- `docs/03_implementation_plan.md`
- `docs/04_implementation.md`
- `prompts/01_requirements.md`
- `prompts/02_design.md`
- `prompts/03_implementation_plan.md`
- `prompts/04_implementation.md`

### Handoff Gate

Chỉ bắt đầu review khi `docs/04_implementation.md` có đúng:

```text
STATUS: PASS
NEXT_PROMPT: prompts/05_review_testing.md
BACKTRACK_REQUIRED: NONE
```

Nếu không đạt, không giả định handoff hợp lệ; ghi rõ lý do và dừng tại bước 05.

## Skills.sh

Trước khi review/testing, đọc hướng dẫn skill từ `skills.sh` hoặc Agent Skills Directory nếu môi trường cho phép. Nếu không thể truy cập, dùng skill agent tương ứng và ghi rõ bằng chứng áp dụng.

| Skill | Mục đích | Nhiệm vụ áp dụng | Thời điểm dùng | Đầu ra mong đợi |
|---|---|---|---|---|
| `code-review` | Tìm bug, regression, thiếu test, lệch spec | Review source theo docs 01-04 | Trước và sau khi chạy test | Findings có severity và evidence |
| `django-security` | Review bảo mật Django | CSRF, XSS, SQL injection, secrets, headers, upload, validation | Security review | Security findings và verified controls |
| `django-expert` | Review kỹ thuật Django | Structure, ORM, migrations, routing, services, tests | Technical review | Django-specific findings |
| `diagnosing-bugs` | Debug lỗi | Chẩn đoán test fail hoặc runtime issue | Khi verification fail | Root cause, fix và retest evidence |
| `tdd` | Regression test cho defect | Thêm failing test trước khi fix nếu khả thi | Khi sửa defect | Regression test chứng minh fix |

Trong `docs/05_review_testing.md` phải có mục `Skills.sh Evidence`, ghi rõ:

- skill đã dùng;
- nhiệm vụ áp dụng;
- artifact hoặc finding tạo ra;
- vị trí bằng chứng trong review report.

## Scope

- Code review.
- Review architecture compliance.
- Review requirements/design/plan compliance.
- Review Django structure, ORM, migrations, routing và services.
- Security review.
- Unit, integration, API, functional, regression và smoke tests.
- Review authentication và role/permission.
- Review domain nghiệp vụ chăn nuôi.
- Review dữ liệu AI, AI provider boundary, output validation và safety notice.
- Review dashboard Bootstrap 5 và frontend scaffold đúng scope.
- Xác định defect.
- Fix defect chỉ khi defect thuộc implementation và không làm thay đổi requirements/design/plan.
- Retest và regression verification.

## Out of Scope

- Không phát triển tính năng mới.
- Không tự bổ sung nghiệp vụ chăn nuôi chưa có trong Requirements.
- Không sửa Requirements/Design/Implementation Plan để hợp thức hóa lỗi code.
- Không tự đổi SQLite sang hệ quản trị khác.
- Không thay đổi API contract hoặc UI scope để che defect.
- Không đặt `PASS` khi còn `BLOCKER` hoặc `CRITICAL` chưa được xử lý.
- Nếu defect thuộc Requirements/Design/Plan, phải ghi `BACKTRACK_REQUIRED` thay vì tự đổi scope.
- Deployment public lên Internet không được dùng để che hoặc bỏ qua lỗi local; chỉ đánh giá deployment khi có artifact deployment thực tế trong phạm vi đã được phê duyệt.

## Tasks

1. Đọc và xác nhận toàn bộ docs 01-04 cùng source code/tests.
2. Kiểm tra handoff gate của bước 04.
3. Áp dụng workflow:

```text
Xác định nhiệm vụ review/testing
-> Chọn skill
-> Đọc hướng dẫn skill
-> Review source/artifacts
-> Lập test plan
-> Run tests
-> Ghi defects
-> Fix defect trong scope nếu có
-> Retest
-> Regression
-> Security regression
-> Coverage review
-> Quality Gate
```

4. Review project structure, Django apps/routes, models/relations, API contract, business rules, validation, authentication/permission, dashboard Bootstrap 5, frontend scaffold scope, SQLite path, secrets, logging và test coverage.
5. Review ba chức năng AI theo đúng Requirements:
   - AI nhắc lịch chăm sóc/tiêm phòng.
   - AI tóm tắt tình trạng đàn từ nhật ký chăm sóc.
   - AI sinh báo cáo tăng trưởng và gợi ý điểm cần theo dõi.
6. Xác minh dữ liệu gửi tới AI nằm trong phạm vi quyền của người dùng.
7. Xác minh safety notice: AI chỉ mang tính tham khảo, không chẩn đoán bệnh và không thay thế bác sĩ thú y/kỹ sư chăn nuôi.
8. Tạo issue table:

```text
Issue ID | Severity | File | Line | Evidence | Problem | Impact | Recommendation | Status
```

Severity hợp lệ:

```text
BLOCKER | CRITICAL | MAJOR | MINOR | INFO
```

9. Tạo coverage table:

```text
Requirement ID | Implementation Evidence | Test Case ID | Test Type | Test Result | Notes
```

10. Nếu sửa defect implementation, tạo fix log:

```text
Issue ID | Root Cause | Files Changed | Fix Summary | Retest Command | Retest Result
```

## Review Checklist

### 1. Requirements / Design / Plan Compliance

- Mỗi MUST requirement có implementation evidence và test/verification tương ứng.
- Không có chức năng code được thêm ngoài scope mà không có nguồn Requirement/Design/Plan.
- Cấu trúc code không mâu thuẫn với architecture và module boundary.
- API contract, permission, validation và error behavior khớp Design.
- SQLite được cấu hình đúng theo Design hiện hành.

### 2. Domain nghiệp vụ

Kiểm tra tối thiểu:

- `Herd`, `Animal`, `AnimalGroup`, `Pen`.
- Nhật ký chăm sóc, thức ăn, thuốc, vaccine.
- Tăng trưởng và sinh sản.
- Xuất bán và doanh thu.
- Thống kê tăng trưởng, chi phí và tỷ lệ hao hụt.
- Không tạo quan hệ hoặc trạng thái nghiệp vụ trái với Design.

### 3. Authentication / Authorization

- Đăng nhập hợp lệ/không hợp lệ.
- Role `quản lý`, `kỹ thuật viên`, `nhân viên`.
- Truy cập trái quyền bị từ chối.
- Dữ liệu trả về không vượt quá phạm vi quyền.
- Không có endpoint bỏ qua permission bằng đường dẫn phụ.

### 4. API / Validation / Error Handling

- HTTP method, status code và response structure đúng Design.
- Server-side validation hoạt động.
- Input thiếu, sai kiểu, sai giá trị hoặc sai quan hệ được xử lý an toàn.
- `400/401/403/404` có behavior rõ ràng.
- Lỗi server không làm ứng dụng crash và không lộ stack trace/secret.

### 5. Security

Kiểm tra tối thiểu:

- CSRF cho flow phù hợp.
- XSS và cách render dữ liệu người dùng.
- Không dùng SQL raw không cần thiết hoặc unsafe.
- Không hard-code API key, password hoặc secret thật.
- Secret được lấy từ environment/config an toàn.
- Upload validation nếu implementation có upload surface.
- Không mở CORS hoặc endpoint rộng hơn Design nếu không có lý do được phê duyệt.

### 6. AI

- AI reminder nhận dữ liệu lịch chăm sóc/vaccine hợp lệ.
- Herd summary nhận nhật ký chăm sóc đúng phạm vi.
- Growth report nhận dữ liệu tăng trưởng/thống kê đúng phạm vi.
- Provider được gọi qua boundary/adapter theo Design.
- Unit test dùng mock provider, không phụ thuộc API thật.
- Timeout, exception, response rỗng hoặc malformed có fallback/error handling.
- Output không được trình bày như chẩn đoán chuyên môn.
- Safety notice xuất hiện ở nơi người dùng nhìn thấy kết quả AI.
- Dữ liệu AI bị giới hạn theo permission của người dùng.

### 7. Dashboard / UI

- Bootstrap 5 được sử dụng theo Design.
- UTF-8 tiếng Việt hiển thị đúng.
- Có trạng thái loading/empty/error phù hợp với phạm vi implementation.
- Dữ liệu hệ thống và kết quả AI được phân biệt rõ.
- Không để frontend scaffold gọi CRUD API thật ngoài scope đã duyệt.

## Verification Commands

### Backend tối thiểu

```powershell
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

### Deployment-oriented Django check

Chỉ dùng khi phần deployment đã được cấu hình trong source/config:

```powershell
python manage.py check --deploy
```

Nếu command này sinh cảnh báo do môi trường local/dev, phải ghi rõ đó là warning môi trường hay defect ứng dụng; không được tự động coi mọi warning là BLOCKER.

### Frontend scaffold

Nếu `frontend/` tồn tại theo Design:

```powershell
cd frontend
npm install
npm run build
```

### Seed / smoke data

Nếu `seed_demo` đã được implementation theo Plan:

```powershell
cd backend
python manage.py seed_demo
```

Sau đó kiểm tra một smoke flow tối thiểu: đăng nhập -> xem dữ liệu -> tạo/cập nhật bản ghi phù hợp -> xem thống kê -> thử chức năng AI bằng dữ liệu demo.

### Security scan gợi ý

```powershell
rg -n "csrf_exempt|mark_safe|\|safe|raw\(|extra\(|Access-Control-Allow-Origin|SECRET_KEY|PASSWORD|TOKEN" backend frontend
```

Kết quả `rg` chỉ là bằng chứng sàng lọc; reviewer phải đọc ngữ cảnh từng match để phân biệt code hợp lệ, placeholder, environment variable và secret thật.

## Test Case Structure

Mỗi test case phải có tối thiểu:

```text
Test Case ID | Requirement ID | Preconditions | Steps | Expected Result | Test Result | Evidence
```

Test Result hợp lệ:

```text
PASS | FAIL | BLOCKED | NOT RUN
```

Ưu tiên coverage cho:

- authentication/authorization;
- CRUD domain chính;
- vaccine/alert;
- growth/reproduction;
- sale/revenue;
- statistics;
- AI reminder/summary/report;
- AI error handling;
- data-scope/security;
- regression và smoke.

## Quality Gate

`docs/05_review_testing.md` chỉ được đặt:

```text
STATUS: PASS
```

khi đồng thời thỏa tất cả:

- Không còn `BLOCKER` hoặc `CRITICAL` chưa xử lý.
- `MAJOR` đã fix hoặc có quyết định chấp nhận được ghi rõ lý do và ảnh hưởng.
- Verification command quan trọng đã PASS hoặc limitation đã được ghi rõ, giải thích được.
- Security review không còn issue nghiêm trọng chưa xử lý.
- Coverage truy vết được từ Requirement đến Test Case và Test Result cho các MUST requirements.
- Không có test fail bị che giấu hoặc đánh dấu PASS sai.
- Có `Skills.sh Evidence`.
- Toàn bộ nội dung UTF-8, tiếng Việt có dấu đúng.

Nếu không đạt:

```text
STATUS: FAIL
```

và phải liệt kê blocking issues, failed tests, limitations hoặc yêu cầu backtrack.

## Traceability

Bước này mở rộng:

```text
Requirement
-> Design Component
-> Implementation Task
-> Source Code
-> Test Case
-> Test Result
```

### Bảng bắt buộc

```text
Requirement ID | Design ID | Task ID | Source Code Evidence | Test Case ID | Test Result
```

## Outputs

Tạo hoặc cập nhật:

- `docs/05_review_testing.md`
- Source code/tests **chỉ khi** sửa defect implementation trong scope.

`docs/05_review_testing.md` phải có:

1. Review Summary.
2. Skills.sh Evidence.
3. Verification Results.
4. Issue Table.
5. Requirement Coverage.
6. Fix Log nếu có.
7. Security Review.
8. Regression Result.
9. Quality Gate.
10. Handoff.

## Final Status Block

Cuối file phải có đúng dạng:

```text
STATUS: PASS | FAIL
NEXT_INPUT: reviewed source code, tests, docs/05_review_testing.md
NEXT_PROMPT: prompts/06_final_delivery.md
TRACEABILITY_MATRIX_UPDATED: YES | NO
BACKTRACK_REQUIRED: NONE | REQUIREMENTS | DESIGN | PLAN | IMPLEMENTATION
```

## Acceptance Criteria

- Review report tồn tại.
- Defect có severity và evidence.
- Tests đã chạy hoặc limitation được ghi rõ.
- Không thêm feature ngoài scope.
- Coverage của MUST requirements có thể truy vết.
- Security review đã thực hiện.
- `NEXT_PROMPT` trỏ đúng `prompts/06_final_delivery.md`.

## Backtrack Rule

- Nếu lỗi thuộc source code/test/config trong phạm vi Implementation: `BACKTRACK_REQUIRED: IMPLEMENTATION`.
- Nếu lỗi thuộc Requirements: `BACKTRACK_REQUIRED: REQUIREMENTS`.
- Nếu lỗi thuộc Design: `BACKTRACK_REQUIRED: DESIGN`.
- Nếu lỗi thuộc Implementation Plan: `BACKTRACK_REQUIRED: PLAN`.
- Nếu toàn bộ review đạt quality gate: `BACKTRACK_REQUIRED: NONE`.

Không được dùng backtrack để tự động thay đổi scope mà không ghi rõ nguyên nhân và artifact cần sửa.

## Handoff to Next Stage

Chỉ chuyển sang `prompts/06_final_delivery.md` khi:

```text
STATUS: PASS
BACKTRACK_REQUIRED: NONE
```

Nếu bước 05 không PASS, phải quay lại đúng artifact bị lỗi trước khi tiếp tục Final Delivery.

## Kết quả Review/Testing thực tế — 2026-09-08

### Review Summary

Source hiện tại đã được đối chiếu với Requirements, Design và Implementation Plan cho TSK-001..TSK-029. Không phát hiện `BLOCKER`, `CRITICAL` hoặc regression implementation còn mở. Review ban đầu ghi nhận thiếu Git repository/history là vấn đề Final Delivery, không phải defect source/test; vấn đề này sau đó được xử lý trung thực trong bước chuẩn bị TSK-030 bằng repository và các commit mới tại thời điểm bàn giao.

### Skills.sh Evidence

Các package skill `code-review`, `django-security` và `django-expert` không được cung cấp trong danh sách skill runtime của phiên kiểm tra. Các checklist tương ứng được thực hiện trực tiếp bằng source review, targeted pattern scan, Django tests, system check, migration inspection và frontend build; không ghi nhận giả rằng skill package đã được chạy.

### Verification Results

| Check | Evidence | Result |
|---|---|---|
| Backend regression | `python manage.py test apps --verbosity 1` — 249/249 | PASS |
| Focused security | auth/RBAC/error/AI/dashboard/seed — 57/57 | PASS |
| Django check | `python manage.py check` — 0 issues | PASS |
| Migration drift | `makemigrations --check --dry-run` — No changes detected | PASS |
| Migration state | `showmigrations` — tất cả expected migrations `[X]` | PASS |
| Seed demo | chạy hai lần; exact reserved counts, non-demo preservation | PASS |
| Frontend build | `npm run build` | PASS |

### Issue Table

Không có defect implementation/test/config nghiêm trọng còn mở. Git history từng được chuyển sang Final Delivery và đã được giải quyết tại bước chuẩn bị TSK-030; không backdate hoặc tạo lịch sử giả.

### Security Review

Authentication, server-side RBAC, precedence/no-role semantics, CSRF, XSS escaping, safe error disclosure, environment-backed secrets, AI data/output boundary và demo-seed safety đều PASS. Không có secret thật được phát hiện trong source/config public.

### Regression Result và Handoff

```text
STATUS: PASS
NEXT_INPUT: reviewed source code, tests, 05_review_testing_chan_nuoi_ai_final.md
NEXT_PROMPT: 06_final_delivery_chan_nuoi_ai_final.md
TRACEABILITY_MATRIX_UPDATED: YES
BACKTRACK_REQUIRED: NONE
```
