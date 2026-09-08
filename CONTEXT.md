# Domain Glossary — Hệ thống quản lý chăn nuôi có tích hợp AI

## Dashboard backend

Trang quản trị do Django render tại `/`, dùng Bootstrap 5 và JavaScript để gọi API cùng origin.

## Frontend scaffold

Cấu trúc Vite/React trong `frontend/` theo `prompts/01_requirements.md`; trong phạm vi bài thực hành, đây là khung giao diện theo Design hiện hành. Không tự triển khai CRUD hoặc gọi API thật nếu Design/Implementation Plan chưa cho phép.

## App users

Django app tại `backend/apps/users/`, phục vụ xác thực và phân quyền người dùng theo các vai trò được Requirements xác định.

## Người dùng

Người sử dụng hệ thống thuộc một trong các vai trò nghiệp vụ đã xác định: `quản lý`, `kỹ thuật viên`, `nhân viên`.

## Đàn vật nuôi

Đơn vị quản lý một nhóm vật nuôi trong trang trại. Đàn có các thông tin nghiệp vụ cần thiết để theo dõi chăm sóc, tăng trưởng, sinh sản, sức khỏe và xuất bán.

## Cá thể vật nuôi

Một vật nuôi được quản lý riêng khi nghiệp vụ cần theo dõi ở mức cá thể.

## Nhóm vật nuôi

Tập hợp vật nuôi được quản lý như một nhóm theo nghiệp vụ. Không tự áp đặt cấu trúc nhóm ngoài Requirements/Design.

## Chuồng trại

Đơn vị không gian dùng để bố trí và quản lý vật nuôi. Thông tin và quan hệ cụ thể phải bám Design.

## Nhật ký chăm sóc

Bản ghi hoạt động chăm sóc vật nuôi/đàn, được sử dụng cho quản lý nghiệp vụ và có thể làm dữ liệu đầu vào cho chức năng AI theo Design.

## Thức ăn

Dữ liệu ghi nhận loại và việc sử dụng thức ăn trong hoạt động chăn nuôi. Không tự mở rộng thành quản lý kho nếu chưa có trong Requirements/Design.

## Thuốc

Dữ liệu ghi nhận việc sử dụng thuốc trong quá trình chăm sóc. Không dùng dữ liệu này để đưa ra chẩn đoán bệnh.

## Vaccine

Dữ liệu về tiêm phòng và lịch tiêm phòng của vật nuôi/đàn.

## Lịch chăm sóc

Các mốc thời gian hoặc hoạt động chăm sóc cần được theo dõi trong hệ thống.

## Cảnh báo lịch

Thông tin nhắc người dùng về lịch chăm sóc, tiêm phòng hoặc kiểm tra sức khỏe theo dữ liệu hệ thống và chức năng được duyệt.

## Tăng trưởng

Thông tin theo dõi sự thay đổi về cân nặng và các số liệu tăng trưởng của vật nuôi/đàn theo thời gian.

## Bản ghi tăng trưởng

Một lần ghi nhận số liệu tăng trưởng của vật nuôi/đàn, phục vụ thống kê và chức năng AI báo cáo tăng trưởng.

## Sinh sản

Thông tin theo dõi các hoạt động và kết quả sinh sản trong phạm vi nghiệp vụ đã được duyệt.

## Xuất bán

Nghiệp vụ ghi nhận vật nuôi/đàn được xuất bán.

## Doanh thu

Giá trị thu được từ nghiệp vụ xuất bán theo dữ liệu hệ thống.

## Chi phí

Các khoản chi phí liên quan đến hoạt động chăn nuôi được hệ thống quản lý trong phạm vi Requirements.

## Tỷ lệ hao hụt

Chỉ số thống kê phản ánh mức hao hụt của đàn theo dữ liệu hệ thống.

## Thống kê tăng trưởng

Các số liệu tổng hợp phục vụ theo dõi tình hình tăng trưởng.

## Thống kê chi phí

Các số liệu tổng hợp về chi phí chăn nuôi trong phạm vi hệ thống.

## AI reminder

Chức năng AI sinh gợi ý nhắc lịch chăm sóc và tiêm phòng từ dữ liệu hệ thống.

## AI herd summary

Chức năng AI tóm tắt tình trạng đàn từ nhật ký chăm sóc và dữ liệu phù hợp trong phạm vi quyền truy cập.

## AI growth report

Chức năng AI sinh báo cáo tăng trưởng và gợi ý điểm cần theo dõi từ số liệu tăng trưởng.

## AI safety notice

Cảnh báo cho người dùng rằng kết quả AI chỉ mang tính tham khảo và không thay thế bác sĩ thú y hoặc kỹ sư chăn nuôi.

## AI provider boundary

Ranh giới/service boundary dùng để gọi AI provider theo Design. Không khóa cứng nhà cung cấp nếu Design chưa quyết định.

## Phân quyền dữ liệu AI

Chỉ dữ liệu nằm trong phạm vi quyền của người dùng được đưa vào chức năng AI.

## SQLite

CSDL được sử dụng cho bản thực hành local theo Design hiện hành tại thời điểm Implementation.

## Pagination

Cách chia dữ liệu danh sách thành nhiều trang theo API/UI Design nếu chức năng này được triển khai.

## Local demo

Bản hệ thống được chạy và kiểm chứng trên máy phát triển bằng Visual Studio Code trước khi xem xét deployment web.

## Web deployment

Việc triển khai hệ thống lên môi trường public. Đây là mục tiêu bổ sung; nếu yêu cầu đổi kiến trúc hoặc database thì phải backtrack theo quy định SDLC.

---

# Context vận hành AI coding agent

## Nguồn ưu tiên

Khi làm việc trên project, ưu tiên tài liệu theo thứ tự:

1. `docs/01_requirements.md`
2. `docs/02_design.md`
3. `docs/03_implementation_plan.md`
4. `docs/04_implementation.md`
5. `docs/05_review_testing.md`
6. `docs/06_final_delivery.md`
7. `CONTEXT.md`
8. `README.md`

`CONTEXT.md` không được dùng để mở rộng scope hoặc ghi đè Requirements/Design/Plan.

## Pipeline

```text
01 Requirements
→ 02 Design
→ 03 Implementation Plan
→ 04 Implementation
→ 05 Review Testing
→ 06 Final Delivery
```

## Quy tắc triển khai

Trước mỗi task phải xác định `Task ID`, `Requirement ID`, `Design ID`, file trong phạm vi task và verification.

Không đổi SQLite, không thêm nghiệp vụ, endpoint hoặc UI ngoài scope nếu chưa có backtrack/approval.

Không tuyên bố `PASS` hoặc `READY` nếu chưa có evidence thực tế.

Local demo phải được kiểm chứng trước; public deployment không được dùng để che lỗi local.

## Trạng thái deployment

Khi chưa có public deployment thật:

```text
DEPLOYMENT_STATUS: NOT_DEPLOYED
```

Không tạo URL giả.
