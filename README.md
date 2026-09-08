# Hệ thống quản lý chăn nuôi có tích hợp AI

Đây là dự án học thuật chạy cục bộ để quản lý dữ liệu chăn nuôi, thống kê từ dữ liệu nguồn và trình bày các báo cáo AI có kiểm soát. Django Dashboard là giao diện chức năng chính; thư mục React/Vite hiện là scaffold và ranh giới tích hợp frontend, không phải một giao diện CRUD nghiệp vụ hoàn chỉnh.

## Chức năng đã triển khai

- Đăng nhập bằng Django session và phân quyền theo vai trò.
- API quản lý đàn, cá thể, nhóm vật nuôi và chuồng.
- API nhật ký chăm sóc, thức ăn và thuốc.
- API lịch vaccine, bản ghi tiêm, tăng trưởng, sinh sản và xuất bán.
- Thống kê tăng trưởng, chi phí, tỷ lệ hao hụt và doanh thu suy ra từ dữ liệu nguồn.
- AI nhắc lịch vaccine, tóm tắt đàn và báo cáo tăng trưởng.
- Django Dashboard tại `/dashboard/`.
- Lệnh `seed_demo` tạo dữ liệu demo xác định, an toàn khi chạy lặp.
- React/Vite scaffold có helper gọi API cùng origin.

## Công nghệ

- Backend: Python, Django, Django REST Framework.
- Cơ sở dữ liệu: SQLite.
- Dashboard: Django Templates, Bootstrap 5.
- Frontend scaffold: React, Vite.
- AI: `AIOrchestrator` và provider adapter trung lập, cấu hình qua biến môi trường.

## Cấu trúc chính

```text
QuanLyChanNuoiGiaSucAI/
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

- Python và `pip`.
- Node.js và npm nếu cần chạy hoặc build React/Vite scaffold.
- PowerShell cho các ví dụ lệnh dưới đây trên Windows.

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

- Backend: `266/266` tests PASS.
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
