# Order Agent

## Mục tiêu
- Tiếp nhận và phân tích các đơn hàng mới để giúp nhân viên giảm thiểu thời gian gõ tin nhắn lại cho từng khách.
- Cảnh báo sớm các đơn vị thiếu thông tin (thiếu hotline, tên món ảo...) để lọc rác hoặc gọi check thủ công nhanh.

## Đầu vào
- Các đơn hàng mới vào trong bảng `Orders` của Notion (với thuộc tính `Status` == `New`).

## Đầu ra
- Nội dung gợi ý chat với khách (`ai_reply_suggestion`).
- Thay đổi `priority` và `tags` tùy thuộc mức độ đầy đủ của đơn hàng.
- Cập nhật record chuyển sang trạng thái mới `Processing` để báo hiệu đã được AI xử lý.

## Quy trình (Flow) chạy
1. Cronjob chạy script `scripts/reply_suggestions.py`.
2. Trích xuất toàn bộ đơn "New" trên Notion.
3. Call API AI (OpenCode) với SystemPrompt đóng vai trò Assistant Sale.
4. Nhận kết quả Format JSON. Cập nhật record lại lên Notion với nội dung Sale cần thiết.
