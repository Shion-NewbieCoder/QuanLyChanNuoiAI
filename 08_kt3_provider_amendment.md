# KT3 Free Live Provider Design Amendment

Task: TSK-KT3-06C. Mode: DOCUMENTATION ONLY.
Baseline: `1c97c6e feat: add AI error contract and safety boundary`.
Decision ID: `PD-KT3-FREE-PROVIDER-001` — APPROVED PROJECT DESIGN DECISION.

## 1. Purpose

Ghi nhận quyết định chuyển primary live provider cho KT3 evaluation sang OpenRouter với một model miễn phí cố định, trước TSK-KT3-07. Đây là amendment hiện tại do con người phê duyệt, không phải yêu cầu vốn được đề bài gốc xác định hoặc bằng chứng đã triển khai/gọi model thành công.

Task này chỉ tạo tài liệu; không sửa source, tests, database, migrations, prompts hoặc launcher, không cài package, gọi mạng/model, tạo key hay commit.

## 2. Reason for Amendment

Theo thông tin đã được project xác nhận trong quá trình chuẩn bị môi trường live, sử dụng OpenAI API trực tiếp cần API billing riêng, không được bao gồm trong ChatGPT Plus. Project có ràng buộc học thuật/demo: ưu tiên inference bằng provider/model có chi phí bằng không khi khả thi, tránh yêu cầu mua OpenAI API credit.

Lựa chọn mới dựa trên endpoint zero-cost và khả năng text generation phục vụ ba feature hiện hữu; model cố định giúp so sánh V1/V2/V3 có ý nghĩa, đồng thời giữ provider abstraction. Đây là căn cứ của quyết định được phê duyệt, không phải xác minh giá, model availability, account access hoặc tương thích API bằng network trong task này. Không bảo đảm free endpoint luôn sẵn sàng hoặc miễn phí vô thời hạn.

OpenAI integration đã thực hiện vẫn hợp lệ, không bị coi là lỗi và không bị loại bỏ.

## 3. Relationship to 07 KT3 Design

Đối với câu hỏi provider-specific của KT3, đọc theo quan hệ:

`07_kt3_ai_integration_design.md` → `08_kt3_provider_amendment.md` → actual source.

Khi 08 xung đột tường minh với 07 về primary live provider cho KT3 evaluation, 08 thắng. Mọi quyết định không liên quan trong 07 tiếp tục authoritative. Actual source là bằng chứng implementation, không tự thay thế approved design.

Không sửa 07, không viết lại lịch sử quyết định KT3 hoặc tài liệu KT1/KT2. Các mô tả trạng thái tại thời điểm soạn 07 được giữ nguyên; amendment này không tuyên bố các trạng thái lịch sử là current runtime status.

## 4. Approved Primary Live Provider

`PD-KT3-FREE-PROVIDER-001` chọn **OpenRouter** làm primary live provider cho KT3 evaluation trong phạm vi học thuật/demo zero-cost.

OpenAI trở thành optional supported adapter, không còn là primary zero-cost KT3 live provider. Không xóa `OpenAIProvider`, tests hoặc cấu hình riêng của adapter; không đánh dấu adapter defective và không viết lại lịch sử công việc đã hoàn thành.

## 5. Fixed KT3 Evaluation Model

Primary fixed live model:

```text
nvidia/nemotron-3-ultra-550b-a55b:free
```

Giữ nguyên identifier này trên các vòng V1/V2/V3 để việc so sánh phản ánh thay đổi prompt trên cùng model. Không dùng automatic/free-model router, automatic model switching hoặc silent fallback sang model khác. Nếu model không khả dụng, ghi nhận failure và báo lại, không tự thay model hay chuyển sang paid inference.

Task này không tạo V2/V3 hoặc prompt-trial evidence; V1 hiện hữu không đổi.

## 6. Provider Architecture

Giữ boundary:

`Feature service → AIOrchestrator → AIProviderInterface → concrete provider`.

Concrete providers có thể gồm `OpenAIProvider` hiện hữu và `OpenRouterProvider` sẽ được triển khai sau. Business feature code không phụ thuộc trực tiếp vendor nào; vendor-specific SDK calls, cấu hình và exception translation nằm sau provider boundary. Fake/mock/injected providers tiếp tục phục vụ automated tests.

## 7. Configuration Contract

Cấu hình dự kiến cho primary KT3 live evaluation, không phải file secrets/runtime config được tạo trong task này:

```text
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=<external secret>
OPENROUTER_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
AI_TIMEOUT_SECONDS=30
AI_MAX_INPUT_BYTES=65536
```

`<external secret>` chỉ là placeholder. Key chỉ cung cấp qua external server-side configuration; không commit, nhúng vào source/DEMO.exe hoặc ghi vào evidence documents. Không tự định nghĩa key fallback/alias giữa OpenRouter, OpenAI và generic key.

Retry policy phải deterministic: không hidden/automatic retries trong academic evaluation. Tên environment variable provider-specific cho retry có thể chốt khi triển khai nếu source yêu cầu; điều này không mở lại policy không retry. Common timeout 30 giây và guard 65,536 bytes giữ nguyên. Cấu hình OpenAI hiện hữu vẫn dành cho optional OpenAI adapter, không bị đổi default hoặc xóa bởi amendment này.

## 8. API / SDK Integration Strategy

Căn cứ tích hợp được quyết định này sử dụng: OpenRouter cung cấp OpenAI-compatible API và Responses API endpoint. Task implementation phải kiểm tra trước liệu OpenAI Python SDK đã cài có hỗ trợ sạch current `PromptSpec` / Responses-style contract với `base_url=https://openrouter.ai/api/v1` hay không. Không coi tuyên bố tương thích là bằng chứng mọi tham số đã được kiểm thử.

Nếu tương thích, ưu tiên tái sử dụng SDK hiện hữu để tránh dependency không cần thiết. Phải bảo toàn system/user/context/output constraints/version, output normalization, error categories, timeout/no-retry và normalized UTF-8 payload guard. Giữ transient-output request policy `store=False`; không được âm thầm bỏ contract chỉ để request chạy được. Đây không phải bảo đảm về mọi chính sách lưu giữ dữ liệu của provider.

Nếu có material incompatibility, STOP và báo lại trong implementation task, không tự bịa mapping, đổi API contract hoặc chọn SDK khác. Task documentation này không chọn/cài dependency, triển khai adapter hoặc thực hiện compatibility/network tests.

## 9. Preserved Feature and Prompt Contracts

Giữ nguyên 07 và các approved contracts liên quan:

- AI Reminder, AI Herd Summary, AI Growth Report; không thêm feature hoặc endpoint.
- DB queries/source selection, exact allowlists, date semantics, source_count và provider-call thresholds.
- Reminder không nguồn không gọi provider; Herd Summary thiếu related records vẫn gọi với Herd facts/lists rỗng; Growth 0/1 record không gọi provider.
- Growth deterministic metric keys/formulas do backend tính; AI không override metrics hoặc business records.
- RBAC, effective-role precedence và no-role denial.
- `PromptSpec`, system/user/context separation, output constraints và V1 definitions: `reminders-v1`, `herd-summary-v1`, `growth-report-v1`.
- Grounding, free-text nguồn là DATA, cảnh báo tham khảo; không diagnosis, treatment recommendation hoặc prediction.
- Output transient: không persist AIRequest/AIResponse, prompt, summary/report, history hoặc provider output vào product database.
- AI error contract và safe Vietnamese presentation: input quá lớn 413; rate limit 429; provider/network hoặc invalid response 502; configuration/invalid model 503; timeout 504. Không secrets/raw provider payload trong public errors/logs.
- Guard 65,536 bytes UTF-8 của normalized provider-bound instructions/user/context: đúng giới hạn được phép, vượt giới hạn không gọi provider; không silent truncation/latest-N.

Không thay đổi business semantics để thích nghi với free-tier limits hoặc availability.

## 10. Privacy and Demo-Data Constraint

KT3 live evaluation trên free endpoint chỉ dùng demo livestock records và synthetic/non-sensitive evaluation data. Không chủ động gửi API keys, passwords, auth/session data, personal information, confidential production information hoặc unrelated database records làm model input. Provider credential chỉ dùng cho server-side request authentication, không là prompt/context/evidence.

Existing application allowlists vẫn bắt buộc. Cần kiểm tra cả nội dung free-text của bộ dữ liệu demo, không chỉ tên field. Ràng buộc academic demo này bổ sung privacy boundary, không thay thế grounding/safety rules hoặc bảo đảm provider không lưu dữ liệu.

## 11. Rate Limit / Availability Constraint

Free-tier inference có rate limits và có thể có availability thấp hơn paid production service. Không suy diễn quota cụ thể hoặc cam kết uptime trong tài liệu này.

TSK-KT3-07 dùng số lần gọi nhỏ, có kiểm soát; ghi trung thực provider/rate-limit failures, không retry lặp lại để che failure. Giữ một model cố định, không automatic switching. Failure không làm đổi feature semantics, không biến thành fake success hoặc fabricated evaluation evidence.

## 12. Portable Demo Boundary

Giữ mục tiêu tương lai đã được project phê duyệt: submitted `DEMO.exe` cuối cùng cho phép evaluator dùng AI mà không phải nhập thủ công provider API key. Distribution/gateway problem thuộc **TSK-KT3-08**, chưa được giải quyết hoặc thiết kế chi tiết trong task này.

Không nhúng `OPENROUTER_API_KEY` hay bất kỳ provider key nào vào executable/source. Không sửa launcher, build EXE hoặc triển khai gateway ở đây. Core management phải tiếp tục hoạt động khi AI chưa được cấu hình/không khả dụng.

## 13. Explicitly Out of Scope

- Source/test/config/launcher modifications, database/schema/migrations hoặc package installation.
- Network/model calls, key creation, live smoke và V1/V2/V3 prompt experiments trong task này.
- Xóa/sửa OpenAI adapter, viết lại historical KT3 decisions hoặc tài liệu KT1/KT2.
- New business rules/features, thay selection/metrics/RBAC/endpoints, persistence hoặc business mutation.
- Diagnosis, treatment recommendations, prediction, automatic model routing/switching hoặc paid fallback.
- Portable distribution/gateway implementation, evidence fabrication và commit.

## 14. Implementation Readiness

Quyết định provider/model đủ rõ để bắt đầu adapter implementation trong task được cấp phép tiếp theo; chưa phải xác nhận OpenRouter đã hoạt động hoặc TSK-KT3-07 đã sẵn sàng gọi live.

Trước TSK-KT3-07 cần:

1. Kiểm tra compatibility của SDK hiện hữu với OpenRouter Responses-style contract; báo blocker nếu không bảo toàn được contract.
2. Triển khai OpenRouter adapter/registration và external configuration theo boundary hiện hữu; chốt tên retry variable nếu cần, giữ no-hidden-retry policy.
3. Chạy fake/mock verification và regression cho mapping, error/safety, size guard, source isolation, thresholds và no mutation; không làm regression phụ thuộc live provider.
4. Chuẩn bị external credential an toàn, synthetic/demo dataset và kiểm tra model access/zero-cost availability trong bước live preparation được cấp phép riêng. Nếu không đáp ứng, báo lại thay vì tự đổi model/provider hoặc trả phí.
5. Chuẩn bị controlled evaluation với fixed model, ghi feature, prompt version, dataset, observed output/failure và human review trung thực. Không ghi secrets; không giả định V2/V3 đã tồn tại.

TSK-KT3-08 tiếp tục giữ phạm vi portable/gateway riêng. Không còn lựa chọn primary provider/model mở trong amendment này; compatibility và live availability vẫn cần verification.

## 15. Superseded Decisions

`PD-KT3-FREE-PROVIDER-001` supersede **chỉ phần lựa chọn OpenAI làm primary live provider KT3** trong `PD-KT3-AI-PROVIDER-001` của 07 (bảng quyết định/mục 5 và các diễn đạt OpenAI-primary cho live evaluation). Primary evaluation target tương ứng nay là OpenRouter với fixed model tại mục 5 của 08, không phải OpenAI default model.

Không supersede toàn bộ `PD-KT3-AI-PROVIDER-001`: provider abstraction, optional OpenAI adapter, SDK boundary, external-secret policy và cấu hình riêng OpenAI tiếp tục hợp lệ. Không đổi lịch sử phê duyệt OpenAI hoặc coi implementation/tests đó là sai.

Các quyết định scope, Growth metrics, prompts, safety, errors, size guard, RBAC, testing/evidence và portable boundary của 07 vẫn có hiệu lực; các constraints demo-data/fixed-model/no-switching và provider config nêu rõ ở 08 áp dụng cho đợt KT3 evaluation mới. Không sửa 07 hoặc bất kỳ file hiện hữu nào trong task này.

STATUS: PROVIDER AMENDMENT READY FOR IMPLEMENTATION
