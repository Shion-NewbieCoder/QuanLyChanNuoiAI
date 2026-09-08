# Hệ thống quản lý chăn nuôi có tích hợp AI

Đây là dự án học thuật chạy cục bộ để quản lý dữ liệu chăn nuôi, thống kê từ dữ liệu nguồn và trình bày các báo cáo AI có kiểm soát. Django Dashboard là giao diện chức năng chính; thư mục React/Vite hiện là scaffold và ranh giới tích hợp frontend, không phải một giao diện CRUD nghiệp vụ hoàn chỉnh.

## Cách chạy dành cho giảng viên

Giải nén đầy đủ bộ nộp bài, giữ nguyên thư mục `DEMO_PORTABLE` và `_internal`
bên trong. Bản portable dành cho Windows x64; Python đã được đóng gói sẵn.
Không cần cài Python, pip, venv, Node/npm, Docker hay quyền quản trị.

**Cách A — mở trực tiếp:** vào `DEMO_PORTABLE`, double-click **DEMO.exe**.
Không cần VS Code và không cần nhập lệnh terminal.

**Cách B — VS Code:** mở thư mục gốc project → nhấn **F5** → chọn
**Run Livestock Management Demo**. Cấu hình gọi cùng `DEMO_PORTABLE/DEMO.exe`
bằng terminal runner có sẵn của VS Code (`node-terminal`); tên runner này
không có nghĩa ứng dụng cần cài Node. Nếu đã tắt bộ JavaScript Debugger tích
hợp của VS Code, bật lại hoặc sử dụng cách A.

EXE tự tạo dữ liệu, chạy migration và seed, rồi mở trình duyệt mặc định tại
`http://127.0.0.1:8000/login/?next=/dashboard/` sau khi HTTP đăng nhập sẵn sàng.
Giữ cửa sổ demo mở trong lúc sử dụng; đóng cửa sổ hoặc nhấn **Ctrl+C** để dừng.
Khi gặp `PORT_UNAVAILABLE`, đóng phiên demo/server cũ rồi chạy lại.

Giao diện quản lý và Bootstrap dùng tài nguyên cục bộ, không cần Internet.
AI chưa cấu hình sẽ hiển thị thông báo an toàn; không có kết quả AI giả.
Dữ liệu được giữ tại `DEMO_PORTABLE/data/db.sqlite3` qua các lần chạy.
Hãy giải nén vào thư mục có quyền ghi và sao lưu tệp này khi cần giữ dữ liệu.

Tài khoản demo:

```text
Username: demo_manager
Password: DemoOnly-2026!
Username: demo_technician
Password: DemoOnly-2026!
Username: demo_employee
Password: DemoOnly-2026!
```

Tài khoản trên chỉ phục vụ chấm bài/thực hành, không dùng cho production.

## Dành cho phát triển mã nguồn

Cần Python 3.12+ để sửa/chạy mã nguồn hoặc build EXE. `RUN_DEMO.bat` vẫn là
tiện ích chạy **mã nguồn** cho lập trình viên: tạo `.venv`, cài requirements,
migrate và seed. Lần cài dependencies đầu cần mạng hoặc pip cache đầy đủ.
F5 hiện chạy bản đã build; sửa mã nguồn xong phải build lại để F5 nhận thay đổi.

Để build trên Windows x64, chạy **BUILD_DEMO.bat** ở gốc dự án. Công cụ dùng
`.venv` phát triển, cài PyInstaller theo `packaging/requirements-build.txt`,
đọc `packaging/DEMO.spec`, tạo `DEMO_PORTABLE/DEMO.exe` cùng runtime bên cạnh.
Đóng EXE trước khi build lại. Build giữ nguyên thư mục `DEMO_PORTABLE/data`;
khi chuẩn bị bản nộp mới, chỉ đưa dữ liệu demo sạch theo chủ ý của bạn.
Giảng viên **không chạy BUILD_DEMO.bat**.

Runtime sinh ra được Git bỏ qua. Nếu chỉ clone Git, lập trình viên phải build
trước; khi nộp bài, đính kèm **toàn bộ DEMO_PORTABLE**, không chỉ tệp EXE.
Mã nguồn dự án vẫn giữ nguyên để xem xét.

Kiểm thử portable dành cho lập trình viên:
`.\.venv\Scripts\python.exe packaging\verify_portable.py`.
Harness sao chép riêng runtime ra TEMP có dấu/khoảng trắng, giới hạn PATH
cho EXE, kiểm tra HTTP/SQLite/process và lưu bằng chứng vào `build/`.
Chi tiết kết quả và giới hạn kiểm chứng: [PORTABLE_DEMO_REPORT.md](PORTABLE_DEMO_REPORT.md).

## Chức năng đã triển khai

- Đăng nhập bằng Django session và phân quyền theo vai trò.
- API quản lý đàn, cá thể, nhóm vật nuôi và chuồng.
- API nhật ký chăm sóc, thức ăn và thuốc.
- API lịch vaccine, bản ghi tiêm, tăng trưởng, sinh sản và xuất bán.
- Thống kê tăng trưởng, chi phí, tỷ lệ hao hụt và doanh thu suy ra từ dữ liệu nguồn.
- AI nhắc lịch vaccine, tóm tắt đàn và báo cáo tăng trưởng.
- Django Dashboard tại `/dashboard/`.
- Giao diện Django đầy đủ cho danh sách, chi tiết, thêm, sửa và xác nhận xóa
  các dữ liệu nghiệp vụ; tìm kiếm/lọc/sắp xếp và nút thao tác theo vai trò.
- Lệnh `seed_demo` tạo dữ liệu demo xác định, an toàn khi chạy lặp.
- React/Vite scaffold có helper gọi API cùng origin.

## Sử dụng giao diện quản lý

Sau F5, đăng nhập bằng tài khoản demo. Sidebar dẫn đến các trang HTML sau,
không cần chạy React/Vite:

| Mục | Đường dẫn |
|---|---|
| Tổng quan | `/dashboard/` |
| Đàn / Cá thể / Nhóm | `/herds/`, `/animals/`, `/animal-groups/` |
| Chuồng trại | `/pens/` |
| Chăm sóc / Thức ăn / Thuốc | `/care/`, `/feed/`, `/medicine/` |
| Lịch vaccine / Lần tiêm | `/vaccines/`, `/vaccination-records/` |
| Tăng trưởng / Sinh sản / Xuất bán | `/growth/`, `/reproduction/`, `/sales/` |
| Thống kê / AI | `/statistics/`, `/ai/` |

Các mục nghiệp vụ có nút **Thêm bản ghi**, **Xem**, **Sửa**, **Xóa** theo quyền.
Xóa cần xác nhận bằng POST; dữ liệu đang được tham chiếu không bị xóa.
Form chuồng yêu cầu đúng một đối tượng đàn/nhóm/cá thể. Form giữ giá trị và
hiển thị lỗi khi dữ liệu không hợp lệ. Trạng thái vaccine có danh mục cố định;
các trường văn bản tự do khác giữ nguyên hợp đồng hiện có.

Trang danh sách gửi `search`, exact filters và `ordering` đến bộ lọc backend
đã có; phân trang 20 dòng. Thống kê tổng hợp toàn bộ dữ liệu đã ghi nhận qua
services hiện có. AI trả kết quả trong trang HTML, không lưu kết quả vào CSDL;
khi chưa có provider, trang hiển thị thông báo an toàn. Không có chatbot hoặc
chức năng chẩn đoán.

CSS có bố cục desktop/tablet/mobile, bảng cuộn ngang và danh mục thu gọn trên
màn hình nhỏ. Bootstrap 5.3.3 được lưu tại `backend/static/vendor/bootstrap/`
kèm giấy phép MIT, dùng được offline. Kiểm thử UI: `python manage.py test apps.dashboard.tests_ui`.
Chi tiết triển khai và xác minh: [UI_COMPLETION_REPORT.md](UI_COMPLETION_REPORT.md).

## Công nghệ sử dụng

- Backend: Python 3.12+, Django 6.1.1, Django REST Framework 3.18.1.
- Cơ sở dữ liệu: SQLite.
- Dashboard: Django Templates, Bootstrap 5.
- Frontend scaffold: React, Vite.
- AI: `AIOrchestrator` và provider adapter trung lập, cấu hình qua biến môi trường.

## Cấu trúc chính

```text
QuanLyChanNuoiGiaSucAI/
├── RUN_DEMO.bat
├── tools/run_demo.py
├── .vscode/launch.json, tasks.json
├── 01_requirements_chan_nuoi_ai.md
├── 02_design_chan_nuoi_ai.md
├── 03_implementation_plan_chan_nuoi_ai_reviewed.md
├── 04_implementation_chan_nuoi_ai_final.md
├── 05_review_testing_chan_nuoi_ai_final.md
├── 06_final_delivery_chan_nuoi_ai_final.md
├── FINAL_REPORT.md
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── config/
│   ├── apps/
│   │   ├── users, herds, pens, care
│   │   ├── vaccinations, growth, reproduction, sales
│   │   └── statistics, ai, dashboard
│   ├── templates/
│   └── static/
└── frontend/
    ├── package.json
    ├── package-lock.json
    ├── vite.config.js
    └── src/
```

Các thư mục `.venv/`, `__pycache__/`, `frontend/node_modules/`, `frontend/dist/`, file `.env` và database SQLite cục bộ được loại khỏi gói mã nguồn bằng `.gitignore`.

## Điều kiện cần

- Giảng viên: Windows x64 và bộ `DEMO_PORTABLE` đầy đủ; trình duyệt mặc định.
- Phát triển mã nguồn/build: Python 3.12+; bootstrap tạo virtual environment
  và cài dependencies khi cần.
- Optional frontend development: Node.js và npm chỉ khi cần chạy/build React/Vite
  scaffold.
- Optional live AI: concrete provider adapter và environment configuration tương
  ứng; không bắt buộc cho dashboard/core demo.
- PowerShell chỉ cần cho các ví dụ development thủ công bên dưới.

Portable và source bootstrap tạo random `DJANGO_SECRET_KEY` chỉ trong process environment,
không in hoặc ghi secret ra file. Django management/dashboard chạy khi
`AI_PROVIDER` và `AI_API_KEY` rỗng; live generation vẫn cần concrete provider
adapter/configuration. Source bootstrap khi thất bại hiển thị
`PYTHON_MISSING`, `VENV_CREATE_FAILED`, `PIP_INSTALL_FAILED`, `MIGRATION_FAILED`,
`SEED_FAILED`, `SERVER_START_FAILED` hoặc `PORT_UNAVAILABLE` cùng next action;
bootstrap không dừng process khác đang chiếm port 8000.

## Cài đặt backend

Từ thư mục gốc dự án:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Biến môi trường

| Biến | Bắt buộc | Mặc định | Mục đích |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | Có, để khởi động Django | Không có | Secret của Django; phải tự đặt ngoài source. |
| `DJANGO_DEBUG` | Không | `false` | Đặt `1` cho môi trường local/demo. |
| `DJANGO_ALLOWED_HOSTS` | Không | `127.0.0.1,localhost` | Danh sách host cách nhau bằng dấu phẩy. |
| `DJANGO_DEMO_DB_PATH` | Không | `backend/db.sqlite3` | Portable tự đặt đường dẫn `data/db.sqlite3` cạnh EXE. |
| `DJANGO_PORTABLE_DEMO` | Không | `false` | Portable tự bật thẻ thông tin tài khoản demo trên trang đăng nhập. |
| `AI_PROVIDER` | Không để khởi động; cần cho live AI | Rỗng | Tên provider adapter đã được đăng ký. |
| `AI_API_KEY` | Không để khởi động; tùy provider live | Rỗng | Credential của provider, không lưu trong source. |

Ví dụ cấu hình local trong phiên PowerShell hiện tại:

```powershell
$env:DJANGO_SECRET_KEY = "<your-local-secret>"
$env:DJANGO_DEBUG = "1"
$env:DJANGO_ALLOWED_HOSTS = "127.0.0.1,localhost"
```

`backend/.env.example` là mẫu tên biến. Source hiện tại dùng `os.getenv` và **không tự động nạp file `.env`**; cần export biến trong shell hoặc dùng công cụ quản lý environment của máy chạy. Không đưa secret thật vào README, source hoặc Git.

## Database, dữ liệu demo và chạy Django

Sau khi đã đặt `DJANGO_SECRET_KEY` và đang ở `backend/`:

```powershell
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000
```

`seed_demo` chỉ chạy khi `DJANGO_DEBUG=1`; lệnh từ chối khi `DEBUG=False`, không flush dữ liệu ngoài demo và an toàn khi chạy lặp.

Các URL chính:

- Đăng nhập: `http://127.0.0.1:8000/login/`
- Dashboard: `http://127.0.0.1:8000/dashboard/`
- API nghiệp vụ: `http://127.0.0.1:8000/api/`

### Truy vấn danh sách API

Các list endpoint nghiệp vụ hỗ trợ `?search=<text>`, exact filters theo
từng resource và `?ordering=<field>`/`?ordering=-<field>`. Các field được
phép:

| Resource | Search | Exact filters | Ordering |
|---|---|---|---|
| Herd | `code`, `name`, `animal_type`, `status` | `status`, `animal_type`, `management_mode` | `code`, `name`, `quantity` |
| Animal | `code`, `status` | `herd`, `status` | `code` |
| AnimalGroup | `code`, `name`, `status` | `herd`, `status` | `code`, `name`, `quantity` |
| Pen | `code`, `name`, `location`, `description`, `status` | `herd`, `animal_group`, `animal`, `status` | `code`, `name` |
| CareLog | `activity`, `notes` | `herd` | `recorded_at` |
| FeedRecord | `feed_type`, `notes` | `herd` | `recorded_at`, `quantity` |
| MedicineRecord | `medicine`, `notes` | `herd` | `recorded_at`, `dose` |
| VaccineSchedule | `vaccine` | `target`, `status` | `scheduled_date`, `vaccine` |
| VaccinationRecord | `notes` | `schedule` | `actual_date` |
| GrowthRecord | `notes` | `target` | `measurement_date`, `weight` |
| ReproductionRecord | `event_type`, `result`, `notes` | `target` | `event_date` |
| SaleRecord | `notes` | `target` | `sale_date`, `amount` |

Các tham số có thể kết hợp trên cùng request. Query chỉ giới hạn
kết quả mà role hiện tại được phép đọc; nó không thay đổi RBAC.

## Tài khoản demo

Các tài khoản được tạo bởi `python manage.py seed_demo` chỉ dành cho demo học thuật cục bộ:

| Username | Vai trò | Password |
|---|---|---|
| `demo_manager` | quản lý | `DemoOnly-2026!` |
| `demo_technician` | kỹ thuật viên | `DemoOnly-2026!` |
| `demo_employee` | nhân viên | `DemoOnly-2026!` |

Đây là credential demo công khai theo `PD-SEED-001`, không phải credential production và không được dùng để suy ra tài khoản production.

## Phân quyền

Phân quyền được kiểm tra ở backend; việc ẩn nút trên giao diện không thay thế authorization.

- Quản lý: CRUD rộng trên tài nguyên nghiệp vụ hiện có.
- Kỹ thuật viên: đọc dữ liệu master; có quyền tác nghiệp create/read/update ở care, vaccine, growth và reproduction; không được xóa.
- Nhân viên: đọc dữ liệu master, vaccine, growth, reproduction và sales; có thể create/read care; không được update/delete care.
- Statistics và AI: chỉ quản lý và kỹ thuật viên.
- Delete trên tài nguyên nghiệp vụ hiện có: chỉ quản lý.
- User không có vai trò được công nhận: bị từ chối trên business API, Statistics và AI.
- Nếu có nhiều vai trò, precedence là `quản lý > kỹ thuật viên > nhân viên`.

## Chức năng AI

Các endpoint hiện có:

```text
POST /api/ai/reminders
POST /api/ai/herd-summary
POST /api/ai/growth-report
```

AI chỉ nhận factual data đã được giảm thiểu theo contract và quyền người dùng. Output chỉ dùng để trình bày, không thay đổi business record, không ghi lịch sử AI vào database và luôn qua validation/safety boundary. `source_count`, các metric tăng trưởng và phân loại lịch vaccine do application kiểm soát, không do AI quyết định.

Project có thể khởi động, chạy dashboard, seed và tests khi chưa cấu hình provider. Regression tests dùng fake/injected provider và không gọi mạng. `seed_demo` không gọi AI.

Source hiện tại cung cấp provider-neutral interface nhưng **không đóng gói concrete live-provider adapter/vendor**. Vì vậy live AI cần một adapter được phê duyệt/đăng ký cùng `AI_PROVIDER` và `AI_API_KEY`; nếu chưa có, AI endpoint thất bại an toàn. Không được ghi API key vào source.

## React/Vite scaffold

Giao diện nghiệp vụ chính vẫn là Django Dashboard. Để chạy scaffold frontend riêng:

```powershell
cd frontend
npm install
npm run dev
```

Build production:

```powershell
npm run build
```

Project chưa cấu hình script lint; không có lệnh `npm run lint`. API helper hiện dùng đường dẫn cùng origin, session cookie và CSRF token cho unsafe request.

## Minh chứng sử dụng AI khi lập trình

Các prompt/response tiêu biểu, mapping phần code được hỗ trợ, human review,
correction và test evidence được ghi trung thực tại
[AI_CODING_EVIDENCE.md](AI_CODING_EVIDENCE.md). Tài liệu đó là representative
evidence, không phải transcript đầy đủ và không suy diễn model name,
timestamp hay code ownership.

## Kiểm thử và xác minh

Backend, từ `backend/` với `DJANGO_SECRET_KEY` đã đặt:

```powershell
python manage.py test apps --verbosity 1
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py showmigrations
```

Frontend, từ `frontend/`:

```powershell
npm run build
```

Evidence gần nhất ngày 2026-09-08:

- Backend sau UI pass: `288/288` tests PASS (266 regression cũ + 22 UI).
- Focused UI: `22/22` tests PASS; 15 trang chính đã kiểm tra qua HTTP có đăng nhập.
- Django system check: PASS.
- Migration drift: NONE; toàn bộ migrations đã áp dụng.
- `seed_demo`: PASS và idempotent.
- Security regression: `57/57` focused tests PASS.
- Vite production build: PASS.
- Frontend lint: NOT CONFIGURED.

## Ghi chú bảo mật và giới hạn

- Bản bàn giao hướng tới local academic demo với SQLite; chưa triển khai public production.
- `DJANGO_SECRET_KEY` bắt buộc và phải được đặt qua environment.
- Không có JWT/localStorage token flow; hệ thống dùng Django session.
- CSRF, template autoescaping, server-side RBAC, centralized safe errors và AI output validation đang được áp dụng.
- React/Vite chỉ là scaffold, không phải business UI hoàn chỉnh.
- Live AI chưa khả dụng nếu chưa có concrete provider adapter và credential ngoài source.
- AI chỉ là thông tin tham khảo, không chẩn đoán bệnh hoặc thay thế bác sĩ thú y/kỹ sư chăn nuôi.

```text
DEPLOYMENT_STATUS: NOT_DEPLOYED
```

## Trạng thái quản lý mã nguồn trước khi nộp

Repository Git cục bộ được khởi tạo tại đúng root dự án trong bước chuẩn bị Final Delivery ngày 2026-09-08. Snapshot hiện tại được chia thành các commit mới, có nội dung rõ ràng cho backend, frontend và tài liệu; các commit này không được trình bày như lịch sử phát triển trước đó. Chưa cấu hình hoặc xác minh Git remote/GitHub và đề bài không bắt buộc remote để chạy demo cục bộ.
