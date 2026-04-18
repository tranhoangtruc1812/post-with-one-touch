# Publish Agent

## Mục tiêu
- Tự động đăng các bài viết đã được người quản lý kiểm duyệt (approved).
- Giảm tải việc thao tác thủ công, hỗ trợ hẹn giờ và ghi log.

## Đầu vào (Input)
- Đọc bảng dữ liệu `Posts` trong hệ thống Notion.
- Điều kiện lọc các dòng thoả mãn: 
  - `status == "Draft"`
  - `approved == True`
- Kênh đăng bài (Channel): Facebook, Zalo, Instagram... (tuỳ thuộc cấu hình dòng).

## Đầu ra (Output)
- Trả về kết quả thực hiện của các API nền tảng: thành công/thất bại, Link bài đăng (URL).
- Cập nhật record trong Notion tương ứng: 
  - Gắn `status = "Published"`
  - Điền `post_url = URL thực tế`
  - Đánh dấu `posted_time = THỜI_GIAN_HIỆN_TẠI`

## Logic Flow
1. Cấu hình chạy định kỳ lấy dữ liệu (qua module scheduler của ứng dụng: ví dụ mỗi 2h/lần hoặc lúc 11:30 và 15:00).
2. Publish Agent lấy các bài post chờ xuất bản.
3. Nếu Channel là Facebook (giả lập): thực hiện "đăng".
4. Nếu thất bại, ghi log lỗi ở Console và để nguyên trạng thái nhằm retry.
5. Nếu thành công, call ngược về API Notion cập nhật record.
