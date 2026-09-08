# 06 Final Delivery

## Role

Bạn là Release Reviewer chịu trách nhiệm quyết định **Hệ thống quản lý chăn nuôi có tích hợp AI** có đủ điều kiện bàn giao hay không.

## Objective

Kiểm tra toàn bộ pipeline SDLC, traceability, test results, tài liệu, cấu hình, bảo mật và release readiness của hệ thống sau các bước 01-05. Không phát triển thêm chức năng trong bước này.

Mọi kết luận `READY FOR DELIVERY` phải dựa trên bằng chứng thực tế từ source code, test result, review result, cấu hình và tài liệu; không được suy đoán dựa trên việc project chỉ có đủ file hoặc có thể mở được source code.

## Language

- Toàn bộ prompt, final review, `FINAL_REPORT.md`, phần cập nhật `README.md` và artifact đầu ra phải viết bằng tiếng Việt có dấu, mã hóa UTF-8.
- Giữ nguyên tiếng Anh hoặc ký hiệu kỹ thuật đối với tên file, thư mục, command, endpoint, code, ID, status marker và delivery decision.
- Không để nội dung bị lỗi mã hóa.

## Inputs

- `docs/01_requirements.md`
- `docs/02_design.md`
- `docs/03_implementation_plan.md`
- `docs/04_implementation.md`
- `docs/05_review_testing.md`
- Source code và tests.
- `README.md`
- `FINAL_REPORT.md` nếu đã tồn tại.
- Deployment artifact nếu project có triển khai web thực tế trong phạm vi được phê duyệt.

### Handoff Gate

Chỉ bắt đầu Final Delivery khi `docs/05_review_testing.md` có đúng:

```text
STATUS: PASS
NEXT_PROMPT: prompts/06_final_delivery.md
BACKTRACK_REQUIRED: NONE
```

Nếu không đạt, không giả định handoff hợp lệ; ghi rõ lý do và dừng tại bước 06.

## Skills.sh

Trước khi final review, đọc hướng dẫn skill từ `skills.sh` hoặc Agent Skills Directory nếu môi trường cho phép. Nếu không thể truy cập, dùng skill agent tương ứng và ghi rõ bằng chứng áp dụng.

| Skill | Mục đích | Nhiệm vụ áp dụng | Thời điểm dùng | Đầu ra mong đợi |
|---|---|---|---|---|
| `code-review` | Final readiness review | Đối chiếu source, docs và release checklist | Final source review | Không còn blocker bàn giao |
| `django-security` | Final security checklist | Secrets, DEBUG, CSRF, XSS, upload, dependency risk | Trước delivery decision | Security readiness summary |
| `django-expert` | Final Django operational review | Migrations, settings, tests, run instructions | Operational readiness review | Django app có thể chạy lại |
| `diagnosing-bugs` | Chẩn đoán lỗi final verification | Xác định root cause và bước SDLC cần quay lại | Khi final verification fail | Backtrack decision và evidence |

Trong `docs/06_final_delivery.md` và `FINAL_REPORT.md` phải có mục `Skills.sh Evidence`, trong đó ghi:

- skill đã dùng;
- nhiệm vụ áp dụng;
- artifact/finding hoặc verification được tạo ra;
- vị trí bằng chứng trong final review.

## Scope

- Kiểm tra status của docs 01-05.
- Kiểm tra traceability end-to-end.
- Kiểm tra test results và defect status.
- Kiểm tra source code, dependency, config, database/migration và seed/demo data.
- Kiểm tra authentication/authorization và permission boundary.
- Kiểm tra security checklist.
- Kiểm tra AI integration boundary, safety notice và xử lý lỗi AI.
- Kiểm tra dashboard/API/frontend scaffold theo Design hiện hành.
- Kiểm tra README install/run/test instructions.
- Kiểm tra khả năng chạy lại project từ môi trường mới dựa trên README.
- Kiểm tra deployment artifact và public URL **chỉ khi deployment web đã thực sự được cấu hình và thuộc phạm vi được phê duyệt**.
- Cập nhật final review và final report.
- Kết luận `READY FOR DELIVERY` hoặc `NOT READY FOR DELIVERY`.

## Out of Scope

- Không phát triển tính năng mới.
- Không sửa requirements/design/plan để hợp thức hóa trạng thái release.
- Không bỏ qua issue nghiêm trọng để đánh dấu ready.
- Không tự đổi SQLite sang hệ quản trị khác ở bước Final Delivery.
- Không tự công bố một public URL chưa được triển khai và kiểm chứng thực tế.
- Không coi deployment public là điều kiện bắt buộc nếu nó chưa nằm trong scope đã được phê duyệt.

## Tasks

1. Đọc docs 01-05, source code, tests và README.
2. Xác nhận handoff từ bước 05 hợp lệ.
3. Xác nhận status của từng stage trước khi ra delivery decision.
4. Áp dụng workflow:

```text
Xác định nhiệm vụ final delivery
-> Chọn skill
-> Đọc hướng dẫn skill
-> Review release artifacts
-> Validate traceability
-> Validate tests/security/docs/config
-> Validate run/reproducibility
-> Validate deployment artifact nếu có
-> Chỉnh sửa tài liệu bàn giao nếu cần
-> Quality Gate
-> Delivery Decision
```

5. Validate traceability:

```text
Requirement -> Design Component -> Implementation Task -> Source Code -> Test Case -> Test Result -> Final Delivery
```

6. Kiểm tra readiness của:
   - requirements;
   - design;
   - implementation plan;
   - implementation report;
   - review/testing report;
   - defect/fix status;
   - README;
   - environment/configuration;
   - database/migrations/seed data;
   - security controls;
   - dashboard/API/frontend scaffold;
   - AI functionality and safety controls.

7. Nếu có deployment web thật, kiểm tra thêm:
   - URL có thể truy cập;
   - app khởi động thành công;
   - database connection hoạt động đúng với cấu hình release;
   - static/media behavior phù hợp với deployment design;
   - secret không nằm trong source;
   - health/smoke flow hoạt động;
   - README có hướng dẫn hoặc thông tin deployment cần thiết.

8. Nếu chưa ready, xác định đúng bước SDLC cần quay lại và đặt `BACKTRACK_REQUIRED` tương ứng.

## Release Readiness Checklist

### 1. SDLC Gate

- `docs/01_requirements.md` có `STATUS: PASS`.
- `docs/02_design.md` có `STATUS: PASS`.
- `docs/03_implementation_plan.md` có `STATUS: PASS`.
- `docs/04_implementation.md` có `STATUS: PASS` và `BACKTRACK_REQUIRED: NONE`.
- `docs/05_review_testing.md` có `STATUS: PASS` và `BACKTRACK_REQUIRED: NONE`.
- Các handoff `NEXT_PROMPT` trước đó không bị sai.

### 2. Requirements / Design / Plan Compliance

- Các MUST requirements quan trọng có traceability end-to-end.
- Không có chức năng được triển khai nhưng không có nguồn Requirement/Design/Plan.
- Architecture và module boundary thực tế không mâu thuẫn với Design.
- API contract và permission behavior khớp Design.
- Database và migration khớp Design hiện hành.
- Không tự ý đổi SQLite sang hệ quản trị khác nếu Design chưa được backtrack/duyệt.

### 3. Implementation Readiness

- Source code có thể chạy lại theo README.
- Migrations có thể áp dụng sạch.
- Seed/demo data chạy được nếu đã được Plan/Implementation định nghĩa.
- Không còn dependency bắt buộc nhưng thiếu trong cấu hình cài đặt.
- Không còn file cấu hình quan trọng bị thiếu.
- Không commit secret thật.

### 4. Functional Readiness

Xác minh bằng test result hoặc smoke evidence cho các nhóm nghiệp vụ đã được Requirements xác định:

- Authentication và role/permission.
- Quản lý đàn, cá thể/nhóm vật nuôi.
- Quản lý chuồng trại.
- Nhật ký chăm sóc.
- Thức ăn, thuốc, vaccine.
- Tăng trưởng và sinh sản.
- Cảnh báo lịch tiêm phòng/kiểm tra sức khỏe.
- Xuất bán và doanh thu.
- Thống kê tăng trưởng, chi phí, tỷ lệ hao hụt.

### 5. AI Readiness

Xác minh ba nhóm chức năng AI theo Requirements:

- AI sinh nhắc lịch chăm sóc và tiêm phòng.
- AI tóm tắt tình trạng đàn từ nhật ký chăm sóc.
- AI sinh báo cáo tăng trưởng và gợi ý điểm cần theo dõi.

Kiểm tra thêm:

- AI provider boundary/adapter phù hợp Design.
- API key/secret không lộ trong source.
- Dữ liệu gửi AI nằm trong phạm vi quyền của người dùng.
- Có xử lý lỗi/timeout/response rỗng hoặc malformed theo Implementation/Review.
- Kết quả AI hiển thị cảnh báo rõ ràng.
- Không trình bày AI như công cụ chẩn đoán bệnh.

### 6. Security Readiness

- Secret/config không chứa credential thật trong repository.
- `DEBUG` và cấu hình production/dev được kiểm tra phù hợp với môi trường release.
- Authentication/authorization hoạt động.
- CSRF/XSS/input validation đã được review.
- Upload surface, nếu có, đã được server-side validation.
- Không có endpoint hoặc CORS configuration mở rộng ngoài Design mà không có phê duyệt.
- Dependency/config quan trọng không chứa cấu hình nguy hiểm chưa được giải thích.

### 7. Documentation Readiness

README phải đủ để một người khác có thể:

1. cài dependency;
2. cấu hình environment;
3. tạo/apply database;
4. seed dữ liệu demo nếu cần;
5. chạy backend;
6. chạy frontend/scaffold nếu có;
7. chạy test/verification;
8. truy cập dashboard;
9. biết cách sử dụng chức năng AI;
10. biết limitation/cảnh báo của hệ thống.

### 8. Web Deployment Readiness — Optional

Phần này **không bắt buộc nếu public deployment chưa nằm trong scope được duyệt**.

Nếu có public deployment thật, final review phải có bằng chứng thực tế cho:

- Public URL.
- Thời điểm/phiên bản release được kiểm tra.
- App khởi động thành công.
- Smoke flow qua URL public.
- Database persistence phù hợp với deployment design.
- Secret được cấu hình ngoài source.
- Không dùng deployment để che lỗi local.

Nếu public deployment chưa thực hiện, ghi rõ:

```text
DEPLOYMENT_STATUS: NOT_DEPLOYED
```

và không được vì lý do đó mà đánh `FAIL` cho toàn bộ Final Delivery nếu local release vẫn đáp ứng scope được duyệt.

## Final Verification

### Backend tối thiểu

```powershell
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Nếu project Implementation/Plan đã định nghĩa test suite cụ thể, phải chạy suite đó và đối chiếu evidence thay vì bỏ qua.

### Deployment-oriented Django check

Chỉ chạy khi source/config đã có deployment configuration tương ứng:

```powershell
python manage.py check --deploy
```

Không tự động coi mọi warning của môi trường local là BLOCKER; phải phân biệt warning môi trường với defect release.

### Frontend

Nếu `frontend/` tồn tại và được triển khai trong phạm vi Design/Plan:

```powershell
cd frontend
npm install
npm run build
```

Nếu `frontend/` chỉ là scaffold chưa có triển khai thật, kiểm tra cấu trúc/package/config và xác nhận không vi phạm scope thay vì yêu cầu một frontend production hoàn chỉnh.

### Seed / Smoke

Nếu `seed_demo` đã được implementation theo Plan:

```powershell
cd backend
python manage.py seed_demo
```

Sau đó thực hiện smoke flow tối thiểu phù hợp với project:

```text
Đăng nhập
-> Xem dữ liệu demo
-> Thực hiện một thao tác CRUD hợp lệ
-> Kiểm tra thống kê/dashboard
-> Thử một chức năng AI bằng dữ liệu demo
-> Xác minh safety notice
```

## Final Test Evidence

Mỗi kiểm tra release phải có bằng chứng phù hợp:

```text
Check ID | Scope | Command/Action | Expected Result | Actual Result | Evidence | Status
```

Status hợp lệ:

```text
PASS | FAIL | BLOCKED | NOT RUN
```

Không được chuyển `BLOCKED` hoặc `NOT RUN` thành `PASS` nếu chưa có căn cứ.

## Issue / Exception Handling

Nếu Final Review phát hiện vấn đề:

```text
Issue ID | Severity | Evidence | Impact | Required Action | Backtrack Target | Status
```

Severity hợp lệ:

```text
BLOCKER | CRITICAL | MAJOR | MINOR | INFO
```

Nguyên tắc:

- `BLOCKER`/`CRITICAL`: không thể `READY FOR DELIVERY`.
- `MAJOR`: phải fix hoặc có quyết định chấp nhận được ghi rõ lý do, ảnh hưởng và người/quy trình phê duyệt nếu có.
- `MINOR`: có thể chấp nhận nếu không ảnh hưởng acceptance criteria và được ghi nhận.
- `INFO`: ghi nhận, không tự động chặn release.

## Review / Validation

### Final Quality Gate

Final quality gate chỉ đạt khi đồng thời thỏa tất cả:

- Docs 01-05 đều có `STATUS: PASS`.
- Handoff từ 05 có `BACKTRACK_REQUIRED: NONE`.
- Requirements quan trọng có traceability end-to-end.
- Test results pass hoặc limitation được ghi rõ, đánh giá được ảnh hưởng và chấp nhận được.
- Không còn `BLOCKER` hoặc `CRITICAL` chưa xử lý.
- Security checklist không còn issue nghiêm trọng.
- README và `FINAL_REPORT.md` đủ để người khác chạy lại dự án.
- Source/config/database/migrations không có lỗi release nghiêm trọng chưa xử lý.
- Không thêm feature trong Final Delivery.
- Toàn bộ nội dung tiếng Việt có dấu đúng UTF-8.

Nếu không đạt:

```text
STATUS: FAIL
PROJECT_STATUS: NOT_READY
DELIVERY_DECISION: NOT READY FOR DELIVERY
```

và phải chỉ rõ lý do cùng `BACKTRACK_REQUIRED`.

Nếu đạt:

```text
STATUS: PASS
PROJECT_STATUS: READY
DELIVERY_DECISION: READY FOR DELIVERY
```

## Traceability

Bước này hoàn tất:

```text
Requirement
-> Design Component
-> Implementation Task
-> Source Code
-> Test Case
-> Test Result
-> Delivery Decision
```

### Bảng bắt buộc

```text
Requirement ID | Design ID | Task ID | Code Evidence | Test Result | Delivery Status
```

Mọi `MUST requirement` quan trọng phải có dòng tương ứng hoặc được nhóm theo cách có thể truy vết ngược rõ ràng.

## Outputs

Tạo hoặc cập nhật:

- `docs/06_final_delivery.md`
- `FINAL_REPORT.md`
- `README.md` nếu hướng dẫn install/run/test/release sai hoặc thiếu.

Không tạo source feature mới trong bước này.

## FINAL_REPORT.md Required Structure

`FINAL_REPORT.md` tối thiểu phải có:

1. Thông tin release và trạng thái project.
2. Tóm tắt phạm vi đã bàn giao.
3. Evidence của 01-05.
4. End-to-end traceability summary.
5. Final test/verification results.
6. Security readiness summary.
7. AI readiness summary.
8. Deployment status nếu có.
9. Known limitations.
10. Issue/exception summary.
11. Delivery decision.
12. Skills.sh Evidence.
13. Final Status Block.

## Final Status Block

Cuối `FINAL_REPORT.md` phải có đúng dạng:

```text
STATUS: PASS | FAIL
PROJECT_STATUS: READY | NOT_READY
DELIVERY_DECISION: READY FOR DELIVERY | NOT READY FOR DELIVERY
NEXT_PROMPT: NONE
BACKTRACK_REQUIRED: NONE | REQUIREMENTS | DESIGN | PLAN | IMPLEMENTATION | REVIEW_TESTING
```

Không được đặt `STATUS: PASS` hoặc `PROJECT_STATUS: READY` khi chưa có evidence tương ứng.

## Acceptance Criteria

- Final review tồn tại.
- `FINAL_REPORT.md` tồn tại.
- Delivery decision rõ ràng.
- Có end-to-end traceability cho MUST requirements quan trọng.
- Có final verification/test evidence.
- Có security readiness assessment.
- Có deployment status rõ ràng nếu project có yêu cầu/public deployment.
- Có cơ chế backtrack nếu chưa ready.
- Không thêm source feature trong bước này.
- `NEXT_PROMPT: NONE`.

## Handoff to Next Stage

Đây là stage cuối của pipeline 6 file.

Nếu:

```text
STATUS: PASS
PROJECT_STATUS: READY
DELIVERY_DECISION: READY FOR DELIVERY
BACKTRACK_REQUIRED: NONE
```

thì bàn giao project kèm source code, README, `docs/`, tests và `FINAL_REPORT.md`.

Nếu:

```text
PROJECT_STATUS: NOT_READY
```

thì không bàn giao như một release hoàn chỉnh; quay lại đúng bước được ghi trong `BACKTRACK_REQUIRED`.

## Current Artifact State

File prompt này là **instruction cho Final Delivery**, không phải bằng chứng rằng project hiện tại đã READY. `STATUS` và `PROJECT_STATUS` chỉ được quyết định sau khi 04 và 05 đã chạy thực tế và có evidence.

## Kết quả Final Delivery thực tế — TSK-030 — 2026-09-08

### Skills.sh Evidence

Các package skill `code-review`, `django-security`, `django-expert` và `diagnosing-bugs` không có trong danh sách skill runtime của phiên này. Final review được thực hiện trực tiếp bằng đối chiếu tài liệu/source, full regression, security regression, Django checks, migration inspection, seed verification, frontend build và README runbook audit. Không ghi nhận giả rằng skill package đã được chạy.

### Release Evidence

| Check ID | Scope | Command/Action | Actual Result | Status |
|---|---|---|---|---|
| FD-001 | Backend regression | `python manage.py test apps --verbosity 1` | 249/249 PASS | PASS |
| FD-002 | Security regression | focused auth/RBAC/error/AI/dashboard/seed suite | 57/57 PASS | PASS |
| FD-003 | Django configuration | `python manage.py check` | 0 issues | PASS |
| FD-004 | Migration drift | `makemigrations --check --dry-run` | No changes detected | PASS |
| FD-005 | Migration state | `showmigrations` | Tất cả expected migrations `[X]` | PASS |
| FD-006 | Demo seed | chạy lặp `seed_demo` trong DEBUG=True | Exact counts, idempotent | PASS |
| FD-007 | Frontend | `npm run build` | Vite build thành công | PASS |
| FD-008 | README/runbook | đối chiếu source và command thực tế | Đã cập nhật | PASS |
| FD-009 | Git/source management | `git init`, staged-file/secret audit và commit snapshot hiện tại | Repository đúng root, có commit thật | PASS |

### Issue / Exception

| Issue ID | Severity | Evidence | Impact | Required Action | Backtrack Target | Status |
|---|---|---|---|---|---|---|
| DL-001 | BLOCKER | Ban đầu `PROJECT_GIT=False`, `PARENT_GIT=False`; đề bài yêu cầu “commit rõ ràng” | Từng chặn delivery gate | Đã khởi tạo repository tại project root và tạo các commit snapshot hiện tại, không backdate | Final delivery | RESOLVED |

### Delivery Decision

Implementation, tests, migration, seed, security, dashboard và frontend build đều đạt. Git repository được khởi tạo tại đúng project root trong bước Final Delivery; các commit phản ánh snapshot hiện tại và không giả lịch sử trước đó. Không có blocker bàn giao còn mở.

```text
STATUS: PASS
PROJECT_STATUS: READY
DELIVERY_DECISION: READY FOR DELIVERY
NEXT_PROMPT: NONE
BACKTRACK_REQUIRED: NONE
MANUAL_ACTION_REQUIRED: NONE
```
