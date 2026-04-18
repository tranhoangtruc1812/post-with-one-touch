# Danh sách Agents trong MVP

## 1. Content Agent
**Nhiệm vụ:**
- Đọc thông tin sản phẩm từ bảng Notion `Products`.
- Dựa vào insight gợi ý, sinh 3-5 bài đăng theo chuẩn Format (Hook, Pain, Solution, CTA).
- Lưu kết quả nháp vào bảng `Posts`.

## 2. Publish Agent
**Nhiệm vụ:**
- Lấy các bài có trạng thái `Approved` ở bảng `Posts`.
- Tiến hành "giả lập đăng bài" (hoặc đăng qua webhook/API thật nếu có) theo thời gian trong lịch.
- Cập nhật url và thời gian đã đăng về `Posts`.

## 3. Order Agent
**Nhiệm vụ:**
- Kiểm tra bảng `Orders` lấy các đơn ở trạng thái `new`.
- Phân tích độ ưu tiên, cập nhật tag (ví dụ thiều SĐT thì gán `need_manual_check`, qua 24h thì `high_priority`).
- Sinh mẫu câu trả lời tư vấn gợi ý sẵn cho sales.

## 4. Report Agent
**Nhiệm vụ:**
- Tổng hợp dữ liệu ngày cuối từ `Posts` và `Orders`.
- Đếm số bài đã tạo/đăng, số đơn hàng.
- Tạo báo cáo string format để gửi vào Channel/Log.
