# 01 Requirements

STATUS: PASS

## Role

Bạn là Chuyên viên phân tích nghiệp vụ và Kỹ sư yêu cầu phần mềm trong quy trình phát triển phần mềm bằng AI.

## Objective

Xác định phần mềm cần làm gì đối với đề tài **Hệ thống quản lý chăn nuôi có tích hợp AI**. Tài liệu này chuẩn hóa bối cảnh, phạm vi, actor, yêu cầu chức năng, yêu cầu phi chức năng, quy tắc nghiệp vụ, validation, exception case, use case/user story, acceptance criteria và traceability để có thể chuyển sang bước Design.

Bước Requirements **không thiết kế kiến trúc, schema cơ sở dữ liệu vật lý, API contract chi tiết, UI layout chi tiết và không viết source code**.

## Pipeline

```text
01_requirements.md -> 02_design.md -> 03_implementation_plan.md -> 04_implementation.md -> 05_review_testing.md -> 06_final_delivery.md
```

## Language

- Toàn bộ prompt, nội dung phân tích và artifact đầu ra viết bằng tiếng Việt có dấu, mã hóa UTF-8.
- Giữ nguyên tiếng Anh hoặc ký hiệu kỹ thuật đối với tên file, thư mục, command, endpoint, HTTP method, Requirement ID, Source ID, Use Case ID, status marker và code block.

## Inputs

- Project Brief chính thức: **Hệ thống quản lý chăn nuôi có tích hợp AI**.
- Yêu cầu kỹ thuật được nêu trong Project Brief.
- Cấu trúc và quy định của file Requirements mẫu do giảng viên cung cấp.

## Skills.sh Evidence

| Skill | Nhiệm vụ áp dụng | Đầu ra đã dùng | Vị trí bằng chứng |
|---|---|---|---|
| `software-requirements` | Chuẩn hóa Requirement ID, source trace, priority, status và acceptance criteria | Bảng yêu cầu FR/NFR có ID, nguồn và tiêu chí chấp nhận kiểm thử được | Mục `Source Trace`, `Functional Requirements`, `Non-functional Requirements` |
| `domain-modeling` | Chuẩn hóa thuật ngữ nghiệp vụ và ranh giới nghiệp vụ | Glossary, actor, thuật ngữ đàn/nhóm/cá thể/chuồng/chăm sóc/vaccine/tăng trưởng/xuất bán | Mục `Domain Glossary` và `Scope` |
| `brainstorming` | Phát hiện điểm mơ hồ, giả định và câu hỏi mở trước khi chốt yêu cầu | Assumptions và Open Questions; không âm thầm biến câu hỏi chưa xác nhận thành yêu cầu bắt buộc | Mục `Assumptions` và `Open Questions` |

> Ghi chú: nguồn đề bài chỉ nêu các lựa chọn framework, CSDL và AI engine; chưa xác nhận một lựa chọn công nghệ cụ thể. Vì vậy tài liệu Requirements không tự chốt một framework/model cụ thể ở giai đoạn này.

## Scope

### Trong phạm vi

1. Đăng nhập và phân quyền theo các vai trò được đề bài nêu: quản lý, kỹ thuật viên, nhân viên.
2. Quản lý đàn, cá thể hoặc nhóm vật nuôi.
3. Quản lý chuồng trại và lịch chăm sóc.
4. Ghi nhận thức ăn, thuốc và vaccine.
5. Theo dõi cân nặng, tăng trưởng và sinh sản.
6. Cảnh báo lịch tiêm phòng hoặc kiểm tra sức khỏe.
7. Quản lý xuất bán và doanh thu.
8. Thống kê tăng trưởng, chi phí và tỷ lệ hao hụt.
9. AI sinh nhắc lịch chăm sóc và tiêm phòng.
10. AI tóm tắt tình trạng đàn từ nhật ký chăm sóc.
11. AI sinh báo cáo tăng trưởng và gợi ý điểm cần theo dõi.
12. AI sử dụng dữ liệu hệ thống phù hợp gồm nhật ký, lịch vaccine và số liệu tăng trưởng làm đầu vào.

### Ngoài phạm vi

Các nội dung sau **không được đề bài xác nhận là bắt buộc trong giai đoạn hiện tại** và không được tự coi là yêu cầu:

- Thiết kế phần cứng/IoT theo dõi vật nuôi tự động.
- Chẩn đoán bệnh tự động bằng AI.
- Điều khiển chuồng trại hoặc thiết bị vật lý tự động.
- Tích hợp hệ thống bên ngoài chưa được nêu trong Project Brief.
- Các nghiệp vụ tài chính/kế toán mở rộng ngoài doanh thu từ xuất bán.

## Stakeholders / Actors

| Actor | Mô tả | Nhu cầu chính |
|---|---|---|
| Quản lý | Người quản lý hoạt động trang trại | Quản lý dữ liệu tổng thể, xem thống kê, theo dõi xuất bán/doanh thu và dùng AI hỗ trợ tổng hợp |
| Kỹ thuật viên | Người phụ trách chăm sóc và theo dõi sức khỏe đàn | Ghi nhật ký chăm sóc, vaccine, thuốc, tăng trưởng, sinh sản và nhận cảnh báo/lưu ý |
| Nhân viên | Người thực hiện các tác vụ vận hành được phân công | Cập nhật dữ liệu nghiệp vụ liên quan và xem thông tin cần thiết theo quyền |
| AI Engine | Thành phần hệ thống cung cấp khả năng AI | Nhận dữ liệu đầu vào phù hợp và sinh nhắc lịch, tóm tắt, báo cáo theo ràng buộc |

## Domain Glossary

| Thuật ngữ | Định nghĩa thống nhất |
|---|---|
| Đàn vật nuôi | Tập hợp vật nuôi được quản lý trong trang trại; có thể được tổ chức theo nhóm hoặc theo cá thể. |
| Cá thể vật nuôi | Một con vật cụ thể được quản lý độc lập khi hệ thống áp dụng quản lý ở mức cá thể. |
| Nhóm vật nuôi | Tập hợp vật nuôi được quản lý chung cho một phạm vi nghiệp vụ. |
| Chuồng trại | Khu vực lưu trú/chăn nuôi dùng để tổ chức và theo dõi đàn vật nuôi. |
| Nhật ký chăm sóc | Bản ghi hoạt động chăm sóc, thức ăn, thuốc, vaccine và các thông tin theo dõi liên quan. |
| Vaccine | Thông tin về việc tiêm phòng cho vật nuôi/nhóm vật nuôi, bao gồm lịch liên quan. |
| Tăng trưởng | Diễn biến các chỉ số theo dõi tăng trưởng, trong đó đề bài nêu rõ cân nặng. |
| Sinh sản | Thông tin và sự kiện liên quan đến quá trình sinh sản của vật nuôi. |
| Xuất bán | Nghiệp vụ ghi nhận việc đưa vật nuôi ra khỏi đàn để bán và dữ liệu doanh thu liên quan. |
| Hao hụt | Chỉ số phản ánh tỷ lệ vật nuôi bị mất/giảm số lượng trong phạm vi dữ liệu quản lý của hệ thống. |
| AI nhắc lịch | Kết quả AI gợi ý các lịch chăm sóc/tiêm phòng cần lưu ý dựa trên dữ liệu hệ thống. |
| Tóm tắt tình trạng đàn | Nội dung AI tổng hợp tình trạng đàn từ dữ liệu được cung cấp, không phải chẩn đoán chuyên môn. |
| Báo cáo tăng trưởng | Nội dung AI tổng hợp xu hướng tăng trưởng và điểm cần theo dõi từ số liệu hệ thống. |

## Source Trace

| Source ID | Nguồn | Nội dung nguồn được sử dụng |
|---|---|---|
| SRC-001 | Mô tả bài toán | Trang trại cần quản lý đàn, chuồng, thức ăn, tiêm phòng, tăng trưởng, sinh sản, xuất bán; vấn đề là dễ bỏ sót lịch tiêm và khó đánh giá hiệu quả đàn. |
| SRC-002 | Mục tiêu | Quản lý các dữ liệu chăn nuôi và tích hợp AI để nhắc lịch, tóm tắt tình trạng đàn, sinh báo cáo tăng trưởng. |
| SRC-003 | Yêu cầu chức năng | Đăng nhập/phân quyền, quản lý đàn, chuồng, chăm sóc, thức ăn, thuốc, vaccine, tăng trưởng, sinh sản, cảnh báo, xuất bán, doanh thu, thống kê. |
| SRC-004 | Dữ liệu và AI | Dữ liệu chính gồm đàn, chuồng, nhật ký chăm sóc, thức ăn, vaccine, tăng trưởng, xuất bán; AI nhận nhật ký, lịch vaccine, số liệu tăng trưởng và tạo nhắc lịch, tóm tắt, báo cáo. |
| SRC-005 | Yêu cầu kỹ thuật | Backend được phép dùng FastAPI/Flask/Django; frontend React/Vue/HTML; CSDL SQLite/MySQL/PostgreSQL; AI Engine OpenAI/Gemini/Claude/Hugging Face/Ollama; có cảnh báo AI không thay thế bác sĩ thú y/kỹ sư chăn nuôi. |
| SRC-006 | Mẫu Requirements của giảng viên | Quy định cấu trúc Requirements, Requirement ID, acceptance criteria, assumptions/open questions và quality gate. |

## Functional Requirements

| Requirement ID | Type | Source ID | Priority | Status | Requirement | Acceptance Criteria |
|---|---|---|---|---|---|---|
| FR-AUTH-001 | Functional | SRC-003 | MUST | Proposed | Hệ thống phải hỗ trợ đăng nhập người dùng. | Người dùng cung cấp thông tin xác thực hợp lệ thì đăng nhập thành công; thông tin không hợp lệ thì không được vào khu vực được bảo vệ. |
| FR-AUTH-002 | Functional | SRC-003, PD-ROLE-001 | MUST | Proposed | Hệ thống phải phân quyền tối thiểu cho các vai trò: quản lý, kỹ thuật viên, nhân viên. | Áp dụng matrix hành động ban đầu tại `PD-ROLE-001`; truy cập trái quyền bị từ chối. |
| FR-HERD-001 | Functional | SRC-001, SRC-003 | MUST | Proposed | Người dùng được cấp quyền phải quản lý được đàn vật nuôi. | Có thể tạo, xem, cập nhật thông tin đàn theo dữ liệu hợp lệ; dữ liệu được lưu và hiển thị lại đúng. |
| FR-HERD-002 | Functional | SRC-003 | MUST | Proposed | Hệ thống phải hỗ trợ quản lý vật nuôi ở mức cá thể hoặc nhóm. | Người có quyền có thể tạo, xem hoặc cập nhật dữ liệu vật nuôi ở mức cá thể hoặc nhóm theo phạm vi nghiệp vụ được áp dụng; dữ liệu được lưu và truy xuất đúng. |
| FR-PEN-001 | Functional | SRC-003 | MUST | Proposed | Hệ thống phải quản lý chuồng trại và thông tin gắn với đàn, nhóm hoặc cá thể theo phạm vi quản lý được chọn. | Người có quyền có thể tạo/xem/cập nhật thông tin chuồng và xác định đúng một trong các liên kết hợp lệ: `Herd`, `AnimalGroup`, hoặc `Animal`; không cho phép chuồng không có target hoặc có nhiều target cùng lúc trong phạm vi triển khai ban đầu. |
| FR-CARE-001 | Functional | SRC-001, SRC-003 | MUST | Proposed | Hệ thống phải ghi nhận lịch và nhật ký chăm sóc. | Có thể tạo bản ghi chăm sóc với dữ liệu đầu vào hợp lệ; bản ghi được truy xuất đúng theo đàn/nhóm và thời gian. |
| FR-FEED-001 | Functional | SRC-003, SRC-004 | MUST | Proposed | Hệ thống phải ghi nhận thức ăn đã sử dụng cho hoạt động chăn nuôi. | Có thể lưu thông tin thức ăn theo bản ghi nghiệp vụ và xem lại dữ liệu đã lưu. |
| FR-MED-001 | Functional | SRC-003, SRC-004 | MUST | Proposed | Hệ thống phải ghi nhận thuốc được sử dụng. | Có thể lưu và truy xuất bản ghi thuốc gắn với đối tượng quản lý và thời điểm phù hợp. |
| FR-VAX-001 | Functional | SRC-003, SRC-004 | MUST | Proposed | Hệ thống phải quản lý lịch và kết quả tiêm vaccine. | Có thể tạo/cập nhật lịch tiêm và ghi nhận việc tiêm; dữ liệu có thể truy xuất theo đối tượng và thời gian. |
| FR-GROW-001 | Functional | SRC-003, SRC-004 | MUST | Proposed | Hệ thống phải theo dõi cân nặng và dữ liệu tăng trưởng. | Có thể ghi nhận số liệu cân nặng theo thời điểm và xem lại lịch sử tăng trưởng. |
| FR-REPRO-001 | Functional | SRC-003 | SHOULD | Proposed | Hệ thống phải hỗ trợ ghi nhận thông tin sinh sản theo phạm vi quản lý ban đầu của hệ thống. | Người có quyền có thể tạo và xem các bản ghi sinh sản với target là đàn (`Herd`), bao gồm `event_date`, `event_type` bắt buộc, `result` và `notes` tùy chọn; `event_type` là giá trị văn bản, không giới hạn bởi taxonomy enum mới. |
| FR-ALERT-001 | Functional | SRC-001, SRC-003, SRC-004 | MUST | Proposed | Hệ thống phải cảnh báo lịch tiêm phòng hoặc kiểm tra sức khỏe khi có lịch cần chú ý. | Khi tồn tại lịch đến hạn hoặc sắp đến hạn theo dữ liệu đã lưu, hệ thống hiển thị cảnh báo tương ứng. |
| FR-SALE-001 | Functional | SRC-003 | MUST | Proposed | Hệ thống phải quản lý nghiệp vụ xuất bán vật nuôi. | Người có quyền có thể ghi nhận thông tin xuất bán hợp lệ và xem lại bản ghi. |
| FR-REV-001 | Functional | SRC-003 | MUST | Proposed | Hệ thống phải quản lý doanh thu từ nghiệp vụ xuất bán. | Doanh thu của bản ghi xuất bán được lưu và có thể tổng hợp/tra cứu từ dữ liệu xuất bán. |
| FR-STAT-001 | Functional | SRC-003 | MUST | Proposed | Hệ thống phải cung cấp thống kê tăng trưởng. | Người có quyền xem được thống kê được tính từ dữ liệu tăng trưởng đã lưu. |
| FR-STAT-002 | Functional | SRC-003, PD-OQ-008 | MUST | Proposed | Hệ thống phải cung cấp thống kê chi phí. | Người có quyền xem được tổng chi phí từ `CostRecord.amount`, và có thể xem tổng theo `CostRecord.category`, với lọc ngày tùy chọn theo `cost_date`. |
| FR-STAT-003 | Functional | SRC-003, PD-OQ-007 | MUST | Proposed | Hệ thống phải cung cấp tỷ lệ hao hụt. | Người có quyền xem được tỷ lệ hao hụt từ `HerdLossRecord` đủ điều kiện theo công thức và khoảng báo cáo đã được phê duyệt tại `OQ-007 Resolution`. |
| FR-AI-001 | Functional | SRC-002, SRC-004 | MUST | Proposed | Hệ thống phải tích hợp AI để sinh nhắc lịch chăm sóc và tiêm phòng. | Khi được cung cấp dữ liệu lịch liên quan, chức năng AI trả về danh sách nhắc lịch có ngữ cảnh; kết quả hiển thị trong hệ thống. |
| FR-AI-002 | Functional | SRC-002, SRC-004 | MUST | Proposed | Hệ thống phải tích hợp AI để tóm tắt tình trạng đàn từ nhật ký chăm sóc. | Với dữ liệu nhật ký hợp lệ, AI sinh bản tóm tắt ngắn gọn, dựa trên dữ liệu đầu vào và không chẩn đoán bệnh. |
| FR-AI-003 | Functional | SRC-002, SRC-004 | MUST | Proposed | Hệ thống phải tích hợp AI để sinh báo cáo tăng trưởng và gợi ý điểm cần theo dõi. | Với dữ liệu tăng trưởng hợp lệ, AI sinh báo cáo có nhận xét về diễn biến và điểm cần theo dõi, không trình bày như kết luận chẩn đoán chuyên môn. |
| FR-AI-004 | Functional | SRC-004 | MUST | Proposed | Chức năng AI phải sử dụng dữ liệu phù hợp từ hệ thống như nhật ký, lịch vaccine và số liệu tăng trưởng. | Dữ liệu gửi tới AI được lấy từ phạm vi dữ liệu nghiệp vụ được cho phép; không sử dụng dữ liệu ngoài phạm vi mà người dùng không có quyền truy cập. |
| FR-AI-005 | Functional | SRC-002, SRC-005 | MUST | Proposed | Kết quả AI phải kèm cảnh báo rằng AI chỉ mang tính tham khảo và không thay thế bác sĩ thú y/kỹ sư chăn nuôi. | Tại nơi hiển thị kết quả AI, cảnh báo giới hạn chuyên môn phải xuất hiện rõ ràng. |

## Non-functional Requirements

| Requirement ID | Type | Source ID | Priority | Status | Requirement | Acceptance Criteria |
|---|---|---|---|---|---|---|
| NFR-SEC-001 | Non-functional | SRC-003, SRC-005, PD-ROLE-001 | MUST | Proposed | Hệ thống phải kiểm soát truy cập theo vai trò và không cho phép người dùng truy cập chức năng ngoài quyền. | Thử action ngoài matrix `PD-ROLE-001` phải bị từ chối và không làm lộ dữ liệu không được phép. |
| NFR-SEC-002 | Non-functional | SRC-005 | MUST | Proposed | Thông tin xác thực và khóa truy cập dịch vụ AI phải được bảo vệ, không ghi cứng khóa bí mật vào source code. | Không tìm thấy API key/secret thật trong source code hoặc file công khai của project. |
| NFR-SEC-003 | Non-functional | SRC-004 | MUST | Proposed | AI chỉ được nhận dữ liệu nằm trong phạm vi người dùng được phép sử dụng. | Kiểm thử tài khoản có quyền khác nhau cho thấy dữ liệu gửi AI thay đổi theo quyền truy cập. |
| NFR-REL-001 | Non-functional | SRC-003 | MUST | Proposed | Dữ liệu nghiệp vụ phải được lưu và truy xuất nhất quán. | Sau khi tạo/cập nhật bản ghi, tải lại hoặc truy vấn lại vẫn nhận đúng dữ liệu đã xác nhận. |
| NFR-REL-002 | Non-functional | SRC-005 | MUST | Proposed | Hệ thống phải xử lý lỗi đầu vào và lỗi dịch vụ AI theo cách không làm ứng dụng crash. | Với dữ liệu sai hoặc AI không phản hồi, hệ thống hiển thị thông báo lỗi phù hợp và vẫn giữ trạng thái ứng dụng ổn định. |
| NFR-USAB-001 | Non-functional | SRC-003 | SHOULD | Proposed | Chức năng quản lý và chức năng AI phải được trình bày rõ ràng để người dùng phân biệt dữ liệu hệ thống với gợi ý AI. | Người dùng có thể nhận biết kết quả AI là gợi ý tham khảo và không nhầm với dữ liệu nghiệp vụ gốc. |
| NFR-TECH-001 | Non-functional | SRC-005 | MUST | Proposed | Công nghệ backend, frontend, CSDL và AI phải nằm trong các lựa chọn được Project Brief cho phép, trừ khi có xác nhận bổ sung. | Hồ sơ project không sử dụng stack ngoài phạm vi cho phép mà không có quyết định/nguồn xác nhận tương ứng. |

## Business Rules

| Rule ID | Quy tắc |
|---|---|
| BR-001 | Trong phạm vi triển khai ban đầu, bản ghi chăm sóc phải gắn với `Herd`. Đề bài tổng quát cho phép hệ thống quản lý đàn, cá thể hoặc nhóm vật nuôi, nhưng không xác định rõ target của `CareLog`; dự án chọn phạm vi ban đầu là `CareLog` theo `Herd`. `Animal` và `AnimalGroup` không phải target của `CareLog` trong triển khai ban đầu trừ khi có yêu cầu mở rộng rõ ràng sau này. |
| BR-002 | Lịch vaccine phải xác định được đối tượng áp dụng và thời điểm cần thực hiện. |
| BR-003 | Dữ liệu tăng trưởng phải gắn với đối tượng được theo dõi; thời điểm ghi nhận phải được lưu để theo dõi diễn biến. |
| BR-004 | Xuất bán phải tham chiếu đến đối tượng/vật nuôi hợp lệ đang thuộc phạm vi quản lý trước thời điểm xuất bán. |
| BR-005 | Doanh thu phải gắn với nghiệp vụ xuất bán tương ứng và được suy ra từ `SaleRecord.amount`; không tạo `RevenueRecord` riêng rời trong phạm vi triển khai ban đầu. |
| BR-006 | Tỷ lệ hao hụt chỉ được tính từ `HerdLossRecord` đủ điều kiện, theo `SUM(lost_quantity) / SUM(opening_quantity) * 100`; không suy diễn từ `SaleRecord`, thay đổi `Herd.quantity`, sinh sản hoặc chênh lệch số lượng tùy ý. |
| BR-010 | Chi phí chỉ được tính từ `CostRecord.amount`; không suy diễn chi phí từ `FeedRecord.quantity`, `MedicineRecord.dose` hoặc bản ghi vaccine khi không có `CostRecord` rõ ràng. |
| BR-007 | Kết quả AI là thông tin tham khảo; AI không được trình bày như chẩn đoán bệnh hoặc chỉ định chuyên môn. |
| BR-008 | Dữ liệu truyền cho AI phải nằm trong phạm vi mà người dùng hiện tại được phép truy cập. |
| BR-009 | Khi dữ liệu đầu vào AI thiếu hoặc không đủ cơ sở để kết luận, hệ thống phải thông báo giới hạn thay vì tạo kết luận chắc chắn không có căn cứ. |

## Validation Rules

| Validation ID | Quy tắc kiểm tra |
|---|---|
| VAL-001 | Các trường bắt buộc của từng nghiệp vụ không được để trống. |
| VAL-002 | Các ngày/giờ nghiệp vụ phải ở định dạng hợp lệ và logic theo nghiệp vụ. |
| VAL-003 | Cân nặng và các số liệu tăng trưởng phải là dữ liệu số hợp lệ, không âm nếu nghiệp vụ không cho phép. |
| VAL-004 | Số lượng vật nuôi dùng cho nghiệp vụ phải là số hợp lệ, không âm. |
| VAL-005 | `SaleRecord.amount` và `CostRecord.amount` phải là giá trị số hợp lệ, không âm; `CostRecord.amount` là tổng chi phí của một bản ghi. |
| VAL-010 | `HerdLossRecord` phải có `opening_quantity > 0`, `lost_quantity >= 0`, `lost_quantity <= opening_quantity` và `period_end >= period_start`. |
| VAL-006 | Một lịch vaccine phải tham chiếu tới đối tượng tồn tại trong hệ thống. |
| VAL-007 | Một bản ghi xuất bán phải tham chiếu tới đối tượng tồn tại và phù hợp trạng thái nghiệp vụ. |
| VAL-008 | Dữ liệu gửi cho AI không được vượt quyền truy cập của người dùng hiện tại. |
| VAL-009 | Khi AI trả về kết quả rỗng, lỗi hoặc không đúng cấu trúc mong đợi, hệ thống phải xử lý lỗi và thông báo phù hợp. |

## Exception Cases

| Exception ID | Tình huống | Yêu cầu xử lý |
|---|---|---|
| EX-001 | Người dùng nhập thiếu trường bắt buộc | Từ chối lưu và hiển thị trường cần bổ sung. |
| EX-002 | Người dùng nhập số liệu không hợp lệ | Từ chối dữ liệu không hợp lệ và thông báo nguyên nhân ở mức người dùng có thể hiểu. |
| EX-003 | Người dùng truy cập chức năng không có quyền | Từ chối truy cập; không trả dữ liệu nhạy cảm hoặc dữ liệu ngoài quyền. |
| EX-004 | Dữ liệu tham chiếu không tồn tại | Không tạo bản ghi; thông báo rằng đối tượng tham chiếu không hợp lệ. |
| EX-005 | Dịch vụ AI timeout/lỗi | Không làm ứng dụng crash; ghi nhận lỗi phù hợp và hiển thị thông báo để người dùng biết AI chưa trả kết quả. |
| EX-006 | AI trả về nội dung không phù hợp hoặc không đủ dữ liệu | Không coi là kết luận chuyên môn; yêu cầu người dùng kiểm tra dữ liệu nguồn hoặc thực hiện nghiệp vụ theo quy trình thực tế. |

## Main Use Cases

### UC-01 — Đăng nhập và sử dụng theo vai trò

**Actor:** Quản lý, Kỹ thuật viên, Nhân viên

**Tiền điều kiện:** Tài khoản tồn tại và được cấp quyền.

**Luồng chính:**
1. Người dùng mở hệ thống.
2. Người dùng nhập thông tin xác thực.
3. Hệ thống kiểm tra thông tin.
4. Hệ thống xác định vai trò.
5. Hệ thống cho phép truy cập các chức năng phù hợp.

**Ngoại lệ:** Thông tin xác thực sai hoặc tài khoản không được phép truy cập.

### UC-02 — Quản lý đàn vật nuôi

**Actor:** Quản lý, Kỹ thuật viên, Nhân viên theo quyền

**Luồng chính:**
1. Người dùng mở chức năng quản lý đàn.
2. Chọn thêm/xem/cập nhật bản ghi.
3. Nhập dữ liệu.
4. Hệ thống validate.
5. Hệ thống lưu và hiển thị dữ liệu.

### UC-03 — Quản lý chăm sóc và vaccine

**Actor:** Quản lý, Kỹ thuật viên, Nhân viên theo quyền

**Luồng chính:**
1. Chọn đàn/nhóm/cá thể.
2. Chọn loại nghiệp vụ: chăm sóc, thức ăn, thuốc hoặc vaccine.
3. Nhập dữ liệu và lịch.
4. Hệ thống validate và lưu.
5. Hệ thống dùng dữ liệu lịch phù hợp cho cảnh báo.

### UC-04 — Theo dõi tăng trưởng và sinh sản

**Actor:** Quản lý, Kỹ thuật viên

**Luồng chính:**
1. Chọn đối tượng.
2. Ghi nhận cân nặng/thông tin tăng trưởng hoặc sự kiện sinh sản.
3. Hệ thống validate và lưu.
4. Hệ thống cho phép xem lịch sử theo thời gian.

### UC-05 — Xuất bán và doanh thu

**Actor:** Quản lý, Nhân viên theo quyền

**Luồng chính:**
1. Chọn đối tượng xuất bán.
2. Nhập thông tin xuất bán và doanh thu.
3. Hệ thống validate.
4. Hệ thống lưu nghiệp vụ.
5. Hệ thống cập nhật dữ liệu phục vụ thống kê.

### UC-06 — Nhận nhắc lịch bằng AI

**Actor:** Quản lý, Kỹ thuật viên

**Luồng chính:**
1. Người dùng yêu cầu xem nhắc lịch.
2. Hệ thống lấy lịch chăm sóc/vaccine được phép truy cập.
3. Hệ thống tạo yêu cầu AI theo prompt đã quy định ở bước sau.
4. AI trả về các lịch cần lưu ý.
5. Hệ thống hiển thị kết quả cùng cảnh báo giới hạn.

### UC-07 — Tóm tắt tình trạng đàn bằng AI

**Actor:** Quản lý, Kỹ thuật viên

**Luồng chính:**
1. Người dùng chọn đàn/nhóm.
2. Hệ thống lấy nhật ký chăm sóc phù hợp.
3. Hệ thống gửi dữ liệu được phép cho AI.
4. AI sinh tóm tắt.
5. Hệ thống hiển thị tóm tắt và cảnh báo không chẩn đoán bệnh.

### UC-08 — Sinh báo cáo tăng trưởng bằng AI

**Actor:** Quản lý

**Luồng chính:**
1. Người quản lý chọn phạm vi dữ liệu tăng trưởng.
2. Hệ thống lấy số liệu được phép.
3. Hệ thống gửi dữ liệu cho AI.
4. AI sinh báo cáo và điểm cần theo dõi.
5. Hệ thống hiển thị kết quả dưới dạng tham khảo.

## Assumptions

| Assumption ID | Giả định | Cơ sở |
|---|---|---|
| ASM-001 | Một hệ thống có thể quản lý cả dữ liệu theo cá thể và theo nhóm nếu nhu cầu nghiệp vụ yêu cầu. | Project Brief ghi rõ “cá thể hoặc nhóm vật nuôi”. |
| ASM-002 | Project Brief yêu cầu thống kê chi phí nhưng không định nghĩa cấu trúc chi tiết; cấu trúc được chốt bằng Project Design Decision tại `OQ-008 Resolution`. | Không coi schema/category tại OQ-008 là chi tiết được Project Brief gốc xác định. |
| ASM-003 | “Kiểm tra sức khỏe” được hiểu là một lịch/nhắc việc nghiệp vụ, không phải chức năng chẩn đoán bệnh. | Đề bài yêu cầu cảnh báo lịch kiểm tra sức khỏe và giới hạn AI. |
| ASM-004 | Cảnh báo “sắp đến hạn” cho lịch vaccine dùng quy tắc ngày lịch đã được phê duyệt tại phần `OQ-005 Resolution`; quy tắc này cũng áp dụng cho lịch chăm sóc khi một thực thể lịch chăm sóc được xác định. | Quyết định yêu cầu đã được phê duyệt để giải quyết OQ-005. |

## Open Questions

| OQ-ID | Câu hỏi | Trạng thái |
|---|---|---|
| OQ-001 | Backend cụ thể sẽ chọn FastAPI, Flask hay Django? | Chưa xác nhận |
| OQ-002 | Frontend cụ thể sẽ chọn React, Vue hay HTML? | Chưa xác nhận |
| OQ-003 | CSDL cụ thể sẽ chọn SQLite, MySQL hay PostgreSQL? | Chưa xác nhận |
| OQ-004 | AI Engine cụ thể sẽ chọn OpenAI, Gemini, Claude, Hugging Face hay Ollama? | Chưa xác nhận |
| OQ-005 | Khoảng thời gian thế nào được gọi là “sắp đến hạn” đối với lịch vaccine/chăm sóc? | Đã giải quyết — xem `OQ-005 Resolution`. |
| OQ-006 | Hệ thống sẽ quản lý cá thể ở mức nào đối với từng loại vật nuôi, và có cần mã định danh riêng cho từng cá thể không? | Chưa xác nhận |
| OQ-007 | Công thức tỷ lệ hao hụt được xác định theo công thức nào và theo khoảng thời gian nào? | Đã giải quyết — xem `OQ-007 Resolution`. |
| OQ-008 | Các loại chi phí cần thống kê cụ thể gồm những loại nào? | Đã giải quyết — xem `OQ-008 Resolution`. |
| OQ-009 | Nghiệp vụ sinh sản cần theo dõi những trường dữ liệu nào? | Đã giải quyết — xem `OQ-009 Resolution`. |
| OQ-010 | Xuất bán được tính theo cá thể, theo nhóm, theo số lượng, theo khối lượng hay kết hợp? | Đã giải quyết — xem `OQ-010 Resolution`. |

### OQ-007 Resolution

> Đây là Project Design Decision đã được phê duyệt để giải quyết chi tiết mà Project Brief gốc không xác định.

- `HerdLossRecord` là nguồn dữ liệu hao hụt: `herd -> Herd`, `period_start`, `period_end`, `opening_quantity`, `lost_quantity` bắt buộc; `notes` tùy chọn.
- Một bản ghi đại diện cho quần thể đầu kỳ và số lượng hao hụt của một `Herd` trong một kỳ báo cáo.
- `opening_quantity > 0`; `lost_quantity >= 0`; `lost_quantity <= opening_quantity`; `period_end >= period_start`.
- `loss_rate_percent = SUM(lost_quantity) / SUM(opening_quantity) * 100` và chỉ dùng `HerdLossRecord` đủ điều kiện.
- Lọc theo ngày là tùy chọn bằng `start_date`/`end_date`; chỉ tổng hợp các kỳ có `period_start` và `period_end` nằm trong khoảng yêu cầu. Không có khoảng ngày thì tổng hợp toàn bộ bản ghi đủ điều kiện.
- Không suy diễn hao hụt từ `SaleRecord`, thay đổi `Herd.quantity`, sinh sản hoặc chênh lệch số lượng tùy ý. Sale không phải mortality/loss.
- Không thêm taxonomy lý do hao hụt trong giai đoạn này.

### OQ-008 Resolution

> Đây là Project Design Decision đã được phê duyệt để giải quyết chi tiết mà Project Brief gốc không xác định.

- `CostRecord` là nguồn dữ liệu chi phí: `herd -> Herd`, `cost_date`, `category`, `amount` bắt buộc; `notes` tùy chọn.
- `amount` là tổng chi phí tiền tệ của một `CostRecord` và phải không âm.
- Category ban đầu được phép: `feed`, `medicine`, `vaccine`, `care`, `other`.
- `total_cost = SUM(CostRecord.amount)`; thống kê có thể nhóm tổng theo `CostRecord.category`.
- Lọc theo ngày là tùy chọn bằng `start_date`/`end_date` trên `CostRecord.cost_date`. Không có khoảng ngày thì tổng hợp toàn bộ bản ghi đủ điều kiện.
- Không suy diễn chi phí từ `FeedRecord.quantity`, `MedicineRecord.dose` hoặc bản ghi vaccine nếu không có `CostRecord` rõ ràng.
- Không thêm `unit_price`, `currency`, supplier, invoice, tax, discount hoặc accounting subsystem.

### OQ-009 Resolution

- Triển khai ban đầu của `ReproductionRecord` là theo phạm vi `Herd` và không mở rộng sang `Animal` hoặc `AnimalGroup` cho tới khi có yêu cầu riêng.
- `target` là bắt buộc và tham chiếu đến `Herd`.
- `event_date` là bắt buộc.
- `event_type` là bắt buộc và lưu dưới dạng text thuần túy; dự án hiện tại không định nghĩa taxonomy enum cho sự kiện sinh sản.
- `result` là tùy chọn.
- `notes` là tùy chọn.
- Không thêm trường sinh sản nào khác trong giai đoạn triển khai ban đầu này.
- Quyết định này giải quyết OQ-009 cho TSK-008 và không mở rộng phạm vi sang dữ liệu sinh sản ở mức cá thể hoặc nhóm.

### OQ-010 Resolution

- Triển khai ban đầu của `SaleRecord` là theo phạm vi `Herd` và không mở rộng sang `Animal` hoặc `AnimalGroup` cho tới khi có yêu cầu riêng.
- `target` là bắt buộc và tham chiếu đến `Herd`.
- `sale_date` là bắt buộc.
- `quantity` được hỗ trợ, nhưng là trường tùy chọn trong triển khai ban đầu; không bắt buộc áp đặt cho mọi bản ghi xuất bán.
- `weight` được hỗ trợ, nhưng là trường tùy chọn trong triển khai ban đầu; không bắt buộc áp đặt cho mọi bản ghi xuất bán.
- `amount` là bắt buộc và biểu diễn tổng giá trị tiền mặt của bản ghi xuất bán đó.
- `notes` là tùy chọn.
- `SaleRecord.amount` là số liệu doanh thu được ghi nhận cho bản ghi xuất bán; doanh thu tổng hợp/tra cứu được suy ra từ `SaleRecord.amount` trong phạm vi ban đầu.
- Không tạo model doanh thu độc lập (`RevenueRecord`) trong giai đoạn triển khai ban đầu này.
- Không thêm `unit_price` hoặc `currency` nếu hiện tại không có nguồn xác nhận cụ thể khác trong project.
- Không thêm kiểu mục tiêu xuất bán đa hình; `SaleRecord` chỉ hướng tới `Herd` trong phạm vi ban đầu.

### PD-ROLE-001 — Initial Role Authorization Resolution

> Đây là Project Design Decision đã được phê duyệt để xác định matrix quyền ban đầu; không phải chi tiết được Project Brief gốc xác định.

| Resource / function | Quản lý | Kỹ thuật viên | Nhân viên |
|---|---|---|---|
| Herd, Animal, AnimalGroup, Pen | create, read, update, delete | read | read |
| CareLog, FeedRecord, MedicineRecord | create, read, update, delete | create, read, update | create, read |
| VaccineSchedule, VaccinationRecord | create, read, update, delete | create, read, update | read |
| GrowthRecord, ReproductionRecord | create, read, update, delete | create, read, update | read |
| SaleRecord | create, read, update, delete | read | read |
| Statistics | read/access | read/access | denied |
| AI functions (TSK-020+) | allowed | allowed | denied |

- Với mọi business resource hiện có, `delete` chỉ dành cho quản lý; không thêm soft-delete.
- Scope ban đầu là role-based trên toàn bộ dữ liệu project: role được phép `read` một resource type có thể đọc mọi record của type đó. Không giới hạn theo người tạo và không thêm farm/tenant/team ownership.
- Effective role được xác định theo thứ tự ưu tiên cố định: `quản lý` > `kỹ thuật viên` > `nhân viên`. Nếu người dùng có nhiều recognized role, chỉ recognized role ưu tiên cao nhất quyết định authorization; không union hoặc intersection quyền.
- User đã authenticated nhưng không thuộc recognized role nào bị từ chối mọi protected business API, statistics và future AI access. Authentication đơn thuần không cấp business authorization.
- Role resolution phải kiểm tra thứ tự ưu tiên tường minh trên; không dựa vào database row order, Group primary key, alphabetical ordering hoặc queryset `.first()` không có role priority.
- Data minimization/scope của AI vẫn tuân theo Design AI và các task AI sau này; quyết định này không triển khai AI.
- Quyết định này giải quyết OQ-010 và làm rõ schema ban đầu cho TSK-009, TSK-016, TSK-017 mà không mở rộng ra các nghiệp vụ tài chính/phân tích mới ngoài phạm vi hiện có.

### PD-AI-REMINDER-001 — Initial Reminder Contract

> Đây là Project Design Decision đã được phê duyệt; không phải chi tiết được Project Brief gốc xác định.

- TSK-021 chỉ dùng `VaccineSchedule` làm nguồn reminder. Không dùng `CareLog`, `FeedRecord` hoặc `MedicineRecord` thay cho care schedule; không có `CareSchedule` và care reminder được deferred đến khi có schedule model được phê duyệt.
- `POST /api/ai/reminders` nhận `scope` bắt buộc (`all` hoặc `herd`), `target_id` bắt buộc khi `scope=herd` và phải là `Herd` hợp lệ, cùng `start_date`/`end_date` ISO tùy chọn. `target_id` phải null/omitted khi `scope=all`; nếu có cả hai ngày thì `start_date <= end_date`.
- Lọc inclusive trên `VaccineSchedule.scheduled_date`; không có date range thì dùng mọi record qualifying. Exclude `completed`/`cancelled`; factual target, vaccine, date, persisted status và derived classification do application xác định.
- Không có record qualifying: HTTP 200, không gọi provider và trả `{status: success, feature: reminders, result: {text: "", source_count: 0}, notice: "No qualifying reminder data."}`.
- Success là transient `{status, feature: reminders, result: {text, source_count}, notice}`; không persist `AIRequest`/`AIResponse`, prompt/history hoặc output, và AI không được thay đổi business records.

### PD-AI-HERD-SUMMARY-001 — Initial Herd Summary Contract

> Đây là Project Design Decision đã được phê duyệt; không phải chi tiết được Project Brief gốc xác định.

- `POST /api/ai/herd-summary` nhận bắt buộc `herd_id` tham chiếu `Herd` hợp lệ; không có date filter. Chọn toàn bộ records liên quan thuộc Herd, không latest-N truncation.
- Allowlist: Herd `id`, `code`, `name`, `animal_type`, `management_mode`, `quantity`, `status`; CareLog `recorded_at`, `activity`, `notes`; FeedRecord `recorded_at`, `feed_type`, `quantity`, `notes`; MedicineRecord `recorded_at`, `medicine`, `dose`, `notes`; VaccineSchedule `vaccine`, `scheduled_date`, `status`; VaccinationRecord `actual_date`, `notes`.
- Chỉ dùng Herd, CareLog, FeedRecord, MedicineRecord, VaccineSchedule, VaccinationRecord. Exclude GrowthRecord (reserved TSK-023), ReproductionRecord, SaleRecord, CostRecord, HerdLossRecord, statistics, reminder output và user/auth/group data.
- Empty related data vẫn HTTP 200, gọi provider với Herd facts và lists rỗng; `source_count=0` (không tính Herd) và AI phải nêu related records unavailable, không bịa facts.
- Success transient: `{status: "success", feature: "herd_summary", result: {text, source_count}, notice: "AI-generated summary based on recorded herd data."}`; không persist AIRequest/AIResponse/prompt/output và AI không thay đổi business data.

### PD-AI-GROWTH-001 — Initial Growth Report Contract

> Đây là Project Design Decision đã được phê duyệt; không phải chi tiết được Project Brief gốc xác định.

- `POST /api/ai/growth-report` nhận `herd_id` bắt buộc và `start_date`/`end_date` ISO tùy chọn, độc lập; Herd phải tồn tại và nếu có cả hai ngày thì `start_date <= end_date`.
- Lọc inclusive trên `GrowthRecord.measurement_date`; không boundary thì không lọc và không latest-N cutoff. Chỉ gửi Herd `id`, `code`, `name`; GrowthRecord `measurement_date`, `weight`, `notes`.
- Application tính `record_count`, first/last measurement date và weight, `absolute_change`, `percent_change` khi first weight > 0 (ngược lại null), và `average_weight`; AI không override metrics.
- Với 0 hoặc 1 record: HTTP 200, không gọi provider, text rỗng, source_count bằng record_count, metrics khả dụng và change metrics null, notice `Insufficient growth data to generate an AI growth report.`
- Với từ 2 records: response transient `{status: "success", feature: "growth_report", result: {text, source_count, metrics}, notice: "AI-generated growth report based on recorded growth data."}`.
- Không prediction/forecasting/diagnosis/treatment, persistence hoặc domain mutation. UC-08 nêu Manager là actor/example; authorization thực tế theo PD-ROLE-001: quản lý và kỹ thuật viên allowed, nhân viên/no-role denied.

### PD-SEED-001 — Deterministic Academic Demo Dataset

> Đây là Project Design Decision đã được phê duyệt cho dữ liệu demo; các tài khoản, credential, record và count cụ thể không phải chi tiết do Project Brief gốc xác định.

- TSK-027 cung cấp một bộ dữ liệu academic demo nhỏ, deterministic, đủ cho main CRUD resources, Django Dashboard, vaccination alert/reminder, Herd Summary, Growth Report, thống kê growth/cost/loss và sales/revenue.
- Cơ chế duy nhất là Django management command `python manage.py seed_demo`. Command chỉ dùng cho local/development demo và phải từ chối chạy với thông báo an toàn khi `DEBUG=False`.
- Command phải an toàn khi chạy lặp, dùng transaction khi phù hợp, không flush, không xóa arbitrary data và chỉ tạo/cập nhật rows thuộc reserved demo namespace. Mọi non-demo record phải giữ nguyên.
- Ba Group được bảo đảm tồn tại đúng tên `quản lý`, `kỹ thuật viên`, `nhân viên`. Tạo đúng ba user active, non-superuser, mỗi user chỉ có role tương ứng: `demo_manager`, `demo_technician`, `demo_employee`.
- Cả ba demo user dùng password công khai `DemoOnly-2026!`. Đây là local academic demo credential, không phải production secret và tuyệt đối không tái sử dụng trong production. Không tạo superuser.
- Herd dùng stable identifiers `DEMO-HERD-001` và `DEMO-HERD-002`; các entity có code/name dùng reserved `DEMO-*` identifier hoặc stable combination từ field hiện có. Không thêm field chỉ để seed.
- Sau mỗi lần chạy, reserved demo dataset có chính xác: 2 Herd, 2 AnimalGroup, 2 Animal, 3 Pen, 2 CareLog, 2 FeedRecord, 2 MedicineRecord, 4 VaccineSchedule, 1 VaccinationRecord, 3 GrowthRecord, 1 ReproductionRecord, 2 SaleRecord, 2 HerdLossRecord, 5 CostRecord và 3 demo user. Count này không áp dụng cho non-demo rows.
- `DEMO-HERD-001` là Herd demo chính với factual sources cho Dashboard, Herd Summary, Growth Report, Statistics, Sales/Revenue và Vaccine Reminder. `DEMO-HERD-002` minh họa multiple-Herd, filter/isolation và CRUD/list; không bắt buộc sao chép mọi source record sang Herd này.
- Ba Pen demo lần lượt minh họa đúng ba target form hợp lệ: Herd-only, AnimalGroup-only, Animal-only; mỗi Pen luôn thỏa exactly-one-target XOR.
- Toàn bộ 2 CareLog, 2 FeedRecord và 2 MedicineRecord là factual history của `DEMO-HERD-001`, chỉ dùng field hiện có và không có invented status/workflow.
- Mốc ngày là `anchor_date = timezone.localdate()` tại thời điểm chạy. Khi chạy lặp, command cập nhật chỉ relative dates của reserved demo rows để scenario luôn hiện thời mà không tăng count.
- Bốn VaccineSchedule của `DEMO-HERD-001` gồm: overdue qualifying tại `anchor_date - 7 days`; due-today qualifying tại `anchor_date`; future qualifying tại `anchor_date + 30 days`; completed historical tại `anchor_date - 30 days` với persisted status `completed`. Ba schedule A/B/C chỉ dùng persisted status hợp lệ, nhất quán với VaccineSchedule; không persist derived alert classification. Một VaccinationRecord liên kết completed schedule.
- Ba GrowthRecord của `DEMO-HERD-001` dùng ngày `anchor_date - 60 days`, `anchor_date - 30 days`, `anchor_date` và weight lần lượt `100`, `112`, `125`; không seed prediction/forecast.
- Một ReproductionRecord hợp lệ của `DEMO-HERD-001` dùng `event_type="breeding"` khi field vẫn là free text; không tạo enum.
- Hai SaleRecord của `DEMO-HERD-001` có total `amount` lần lượt `5000000`, `7500000`; revenue vẫn do application suy ra và không tạo RevenueRecord/unit price/currency.
- Hai HerdLossRecord của `DEMO-HERD-001` dùng historical relative periods hợp lệ với `(opening_quantity, lost_quantity)` lần lượt `(100, 2)` và `(98, 1)`; không lưu loss rate.
- Năm CostRecord của `DEMO-HERD-001` dùng historical relative dates, mỗi category đúng một record: `feed=3000000`, `medicine=1200000`, `vaccine=800000`, `care=1000000`, `other=500000`; không lưu precomputed total.
- Tạo đúng 2 AnimalGroup và 2 Animal bằng required fields hiện có, reserved demo codes/names và valid Herd references; không tạo health/breed taxonomy, ownership rule hoặc capacity rule.
- Chỉ seed factual source rows; không seed precomputed statistics, AIRequest/AIResponse, prompt, report, reminder/summary/report text hoặc provider history và không gọi AI provider. Dữ liệu phải qua validation hiện có, không bypass hay nới lỏng invariant.

### OQ-005 Resolution

- Việc phân loại cảnh báo cho lịch vaccine dùng ngày lịch và ngày hiện tại của hệ thống.
- `overdue`: scheduled date < current date.
- `due today`: scheduled date = current date.
- `due soon`: scheduled date > current date và scheduled date <= current date + 7 ngày lịch.
- `scheduled / not-yet-due`: scheduled date > current date + 7 ngày lịch.
- Đây là các phân loại cảnh báo dẫn xuất; không tạo thêm giá trị `VaccineSchedule.status` được lưu ngoài taxonomy status đã được Design xác định.
- Lịch đã completed, cancelled hoặc skipped không được chọn cho cảnh báo đang chờ xử lý.
- Cùng quy tắc ngày dẫn xuất áp dụng cho lịch chăm sóc khi một thực thể lịch chăm sóc được xác định; không áp dụng cho `CareLog`, `FeedRecord` hoặc `MedicineRecord`.

### VaccineSchedule persisted status taxonomy

- `VaccineSchedule.status` là trường trạng thái lifecycle được lưu trong CSDL và có taxonomy cố định:
  - `scheduled`: lịch đã được lập nhưng chưa ở trạng thái due.
  - `due`: lịch đến hạn / cần chú ý theo trạng thái lifecycle của `VaccineSchedule`.
  - `completed`: lịch đã được thực hiện.
  - `cancelled`: lịch đã bị hủy / bỏ qua.
- Không thêm giá trị persisted nào khác cho `VaccineSchedule.status`.
- Các phân loại cảnh báo dẫn xuất theo OQ-005 (`overdue`, `due today`, `due soon`, `scheduled / not-yet-due`) là cảnh báo dẫn xuất, không được lưu vào `VaccineSchedule.status`.
- `cancelled` là trạng thái persisted cho lịch đã hủy/bỏ qua; không tạo status `skipped` riêng nếu không có xác nhận nghiệp vụ riêng biệt.

## Requirement Traceability Matrix

| Source ID | Requirement IDs |
|---|---|
| SRC-001 | FR-HERD-001, FR-PEN-001, FR-CARE-001, FR-ALERT-001 |
| SRC-002 | FR-AI-001, FR-AI-002, FR-AI-003, FR-AI-005 |
| SRC-003 | FR-AUTH-001, FR-AUTH-002, FR-HERD-001, FR-HERD-002, FR-PEN-001, FR-CARE-001, FR-FEED-001, FR-MED-001, FR-VAX-001, FR-GROW-001, FR-REPRO-001, FR-ALERT-001, FR-SALE-001, FR-REV-001, FR-STAT-001, FR-STAT-002, FR-STAT-003 |
| SRC-004 | FR-AI-001, FR-AI-002, FR-AI-003, FR-AI-004 |
| SRC-005 | NFR-SEC-002, NFR-SEC-003, NFR-REL-002, NFR-TECH-001, FR-AI-005 |
| SRC-006 | Toàn bộ cấu trúc Requirement và quality gate của tài liệu |
| PD-OQ-007 | Project Design Decision đã phê duyệt cho nguồn dữ liệu, công thức và kỳ báo cáo tỷ lệ hao hụt; không phải chi tiết được Project Brief gốc xác định. |
| PD-OQ-008 | Project Design Decision đã phê duyệt cho nguồn dữ liệu, category và aggregation chi phí; không phải chi tiết được Project Brief gốc xác định. |
| PD-ROLE-001 | Project Design Decision đã phê duyệt cho matrix action theo vai trò, precedence `quản lý > kỹ thuật viên > nhân viên`, no-role denial, delete restriction và role-wide data scope ban đầu; không phải chi tiết được Project Brief gốc xác định. |
| PD-AI-GROWTH-001 | Project Design Decision đã phê duyệt cho API, date filters, allowlists, deterministic metrics, minimum-data threshold và transient Growth Report; không phải chi tiết được Project Brief gốc xác định. |
| PD-SEED-001 | Project Design Decision đã phê duyệt cho local-only deterministic demo dataset, accounts/credential, reserved counts, relative dates, idempotence và non-demo preservation; không phải chi tiết được Project Brief gốc xác định. |

## Review / Validation

### Kết quả review

- Mỗi yêu cầu quan trọng có Requirement ID ổn định.
- Các yêu cầu chức năng và phi chức năng đều có Source ID.
- MUST requirements có acceptance criteria kiểm thử được.
- Scope và Out of Scope được tách riêng.
- Business Rules, Validation Rules và Exception Cases được tách riêng.
- Các công nghệ chưa được xác nhận không bị tự chốt trong Requirements.
- Các vấn đề chưa được Project Brief xác nhận được ghi thành Assumptions hoặc Open Questions.
- AI có giới hạn rõ: chỉ tham khảo, không chẩn đoán bệnh và phải tôn trọng phạm vi dữ liệu.
- Có traceability từ Source -> Requirement.

**Blocking issues:** Không có blocker bắt buộc phải ngừng bước Requirements.

**Quality Gate:** PASS

## Outputs

Tạo hoặc cập nhật:

```text
docs/01_requirements.md
```

Cuối file phải có:

```text
STATUS: PASS
NEXT_INPUT: docs/01_requirements.md
NEXT_PROMPT: prompts/02_design.md
TRACEABILITY_MATRIX_UPDATED: YES
```

## Acceptance Criteria

- `docs/01_requirements.md` tồn tại.
- Chưa tạo hoặc sửa source code trong bước này.
- Requirements đủ rõ để chuyển sang Design.
- Không còn BLOCKER hoặc CRITICAL trong review yêu cầu.
- `NEXT_PROMPT` trỏ đúng `prompts/02_design.md`.

## Handoff to Next Stage

Chỉ chuyển sang `prompts/02_design.md` khi `docs/01_requirements.md` có `STATUS: PASS`.

NEXT_INPUT: docs/01_requirements.md
NEXT_PROMPT: prompts/02_design.md
TRACEABILITY_MATRIX_UPDATED: YES
