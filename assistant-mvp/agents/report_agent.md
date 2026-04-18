# Report Agent

## Mục tiêu
- Tự động thống kê số liệu hoạt động trong ngày của các Agent khác (số lượng bài viết tạo ra, bài đăng, đơn hàng) và tóm tắt thành báo cáo dễ đọc lúc 20:30 hằng ngày.

## Input (Đầu vào)
- Đếm tổng số bài viết đã tạo trong ngày (Query bảng `Posts`).
- Đếm tổng số bài viết đã đăng thành công trong ngày.
- Đếm số lượng New Orders, Processing Orders.

## Output (Đầu ra)
- Nội dung báo cáo ngắn gọn, hiển thị lên log hoặc gửi sang Mạng xã hội/Telegram/Notion tuỳ hệ thống.
- Báo cáo phải được gen từ AI để tạo giọng điệu tích cực nếu số tốt hoặc cảnh báo nếu có sự bất thường.

## Flow (Luồng)
1. Scheduler gọi `scripts/daily_report.py` lúc 20:30.
2. Script quét Database tổng hợp raw metrics.
3. Call OpenCode API qua `report_prompt.md`.
4. In ra logger / Gửi đi (Webhook).
