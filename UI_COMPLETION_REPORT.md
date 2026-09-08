# Hoàn thiện giao diện Django — 2026-09-08

Đã triển khai trực tiếp trong workspace hiện tại. Phạm vi là giao diện trình
duyệt cho các hợp đồng nghiệp vụ đã có; không thêm model, migration, quy tắc
phân quyền, công thức thống kê hoặc provider AI.

## Nguồn đã đối chiếu

Đề bài Dự Án.txt; 01_requirements_chan_nuoi_ai.md;
02_design_chan_nuoi_ai.md; 03_implementation_plan_chan_nuoi_ai_reviewed.md;
04_implementation_chan_nuoi_ai_final.md; 05_review_testing_chan_nuoi_ai_final.md;
06_final_delivery_chan_nuoi_ai_final.md; README.md; models, serializers,
domain_validation, API viewsets, query filters, role helpers, services thống kê,
AI features và các tests hiện tại.

PD-ROLE-001 tiếp tục quyết định quyền. Pen giữ XOR đúng một đối tượng;
CareLog vẫn chỉ thuộc Herd. Các target của vaccine/tăng trưởng/sinh sản/xuất
bán tiếp tục là Herd. Vaccine giữ bốn trạng thái persisted và dùng helper
hiện có để hiển thị cảnh báo suy ra. Trường văn bản không có choices trong
model vẫn cho phép nhập tự do; không thêm taxonomy mới.

## Màn hình và route

12 nhóm dữ liệu có danh sách, chi tiết, thêm, sửa, xác nhận xóa:

- `/herds/`, `/animals/`, `/animal-groups/`, `/pens/`
- `/care/`, `/feed/`, `/medicine/`
- `/vaccines/`, `/vaccination-records/`
- `/growth/`, `/reproduction/`, `/sales/`

Mỗi route có các đuôi `create/`, `<id>/`, `<id>/edit/`, `<id>/delete/`.
Trang danh sách dùng search/exact filters/ordering từ API viewset tương ứng,
phân trang 20 dòng và giữ tham số khi chuyển trang.

Các trang bổ sung: `/statistics/`, `/ai/`. `/` chuyển về dashboard.
Dashboard và login dùng chung phong cách với header, sidebar, breadcrumb,
cards, bảng, trạng thái trống, thông báo và layout responsive.

Thống kê dùng services hiện có và derive_sales_revenue; tổng số lượng trên
dashboard là tổng Herd.quantity, không cộng trùng số cá thể/nhóm. Giao diện
AI dùng các request serializer và feature function hiện có. Kết quả transient,
được escape và có cảnh báo chuyên môn. Thiếu provider có thông báo an toàn;
không gọi dịch vụ AI thật trong kiểm thử.

## An toàn và xác minh

- Mọi màn hình CRUD kiểm tra quyền phía server bằng RoleActionPermission.
- Form tạo từ các trường model có thể ghi trong serializer, lưu cuối cùng qua
  serializer/domain validation đã có, giữ giá trị khi validation thất bại.
- Xóa chỉ qua POST có CSRF sau trang xác nhận; ProtectedError có thông báo.
- Các lỗi HTML 403/404/500 được trình bày an toàn cả khi demo DEBUG=true.
  Error middleware không thay đổi response API.
- Django auth/session và logout POST được giữ nguyên. Login HTML mang `next`
  về dashboard nếu người dùng mở login trực tiếp; contract POST auth cũ giữ nguyên.

| Kiểm tra | Kết quả |
|---|---|
| Focused UI: `python manage.py test apps.dashboard.tests_ui` | 22/22 PASS |
| Full regression: `python manage.py test apps --verbosity 1` | 288/288 PASS (266 cũ + 22 UI) |
| `python manage.py check` | PASS |
| `python manage.py makemigrations --check --dry-run` | No changes detected |
| HTTP thực qua launcher trên port 8000 | Login, CSRF, 15 trang chính, CSS và logout PASS |
| Marker readiness, server sống sau marker, Ctrl+C Windows | PASS; port được giải phóng |
| Các route CRUD và quyền GET/POST | Django test client PASS |

Focused tests bao gồm CRUD từng loại bản ghi, mọi vai trò và no-role,
Pen XOR, xóa bản ghi đang tham chiếu, giữ input sai, query/filter/ordering,
phân trang, empty state, navigation, CSRF, XSS, safe errors, AI thiếu provider,
thiếu dữ liệu và escape nội dung AI.

## Giới hạn kiểm tra

Không có browser kết nối trong công cụ hiện tại, nên chưa kiểm chứng ảnh
hiển thị ở desktop/tablet/mobile hoặc thao tác F5 trực tiếp trong VS Code.
Responsive đã triển khai bằng CSS media queries; các màn hình được kiểm tra
bằng test client và HTTP thực. Bootstrap tiếp tục dùng CDN 5.3.3 như trước.
Không thay đổi `.vscode/`, `RUN_DEMO.bat` hay `tools/run_demo.py` trong UI pass.

Không tạo ZIP, project copy, React UI, Docker hay deployment.
