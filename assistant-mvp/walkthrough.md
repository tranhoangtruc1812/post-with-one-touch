# Báo cáo Hoàn Thành: Trợ lý AI Bán Hàng MVP

Xin chào bạn, toàn bộ hệ thống Trợ lý MVP đã được xây dựng xong trong thư mục `assistant-mvp` theo đúng yêu cầu thiết kế `mvp_tro_ly_ai_ban_hang.md` gốc.

Cấu trúc hiện diện với 4 agent chạy định kỳ (qua APScheduler), lưu trữ dữ liệu tại Notion, và tận dụng ngôn ngữ AI từ OpenCode (hoặc endpoint chuẩn OpenAI).

## 1. Cấu trúc Source Code đã hoàn tất
- **Core system**: `requirements.txt`, `.env.example`, `app/models.py`, `app/utils.py`, `app/notion_db.py`, `app/opencode_api.py`, `app/scheduler.py`, `app/main.py`.
- **Thư mục Agents (`agents/`)**: Các file quy định Behavior (`content_agent.md`, `publish_agent.md`, `order_agent.md`, `report_agent.md`).
- **Thư mục Prompts (`prompts/`)**: Chứa System/User Prompts để điều khiển mô hình AI (`content_prompt.md`, `order_prompt.md`, `report_prompt.md`).
- **Thư mục Scripts (`scripts/`)**: Cụ thể hóa luồng data của từng tác vụ tự động (`generate_posts.py`, `publish_posts.py`, `sync_orders.py`, `reply_suggestions.py`, `daily_report.py`).

## 2. Hướng dẫn Vận Hành và Kiểm Thử
Vì hệ thống tương tác với Notion API và OpenCode API, bạn cần thiết lập cấu hình môi trường chuẩn:

### Bước 2.1: Khởi tạo thư viện
Mở Terminal, trỏ đường dẫn tới thư mục `assistant-mvp` và chạy:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Bước 2.2: Cài đặt Keys (.env)
1. Đổi tên file `.env.example` thành `.env`.
2. Truy cập Notion, tạo 1 bộ API Integration và cấp quyền cho 3 database: Products, Posts, Orders. Lấy `NOTION_API_KEY` và `Database IDs`.
3. Điền vào `.env`:
```env
NOTION_API_KEY="secret_abc123"
NOTION_PRODUCTS_DB_ID="your_product_db_id"
NOTION_POSTS_DB_ID="your_posts_db_id"
NOTION_ORDERS_DB_ID="your_orders_db_id"

OPENCODE_API_KEY="your_opencode_token"
OPENCODE_API_URL="https://api.opencode.vn/v1/chat/completions" # giữ nguyên hoặc sửa nếu nền tảng thay đổi
```

### Bước 2.3: Khởi động hệ thống
Bạn có thể khởi động App tổng (Scheduler chạy nền hằng ngày) bằng:
```bash
python -m app.main
```
Hệ thống sẽ giữ tiến trình và kích hoạt các cronjob định kỳ. 

👉 **Mẹo**: Nếu bạn muốn chạy test thủ công từng Workflow thay vì đợi mốc giờ (VD xem nó tự thiết kế bài Post hay phân loại Đơn hàng ra sao):
```bash
python -m scripts.generate_posts
python -m scripts.reply_suggestions
python -m scripts.daily_report
```

## 3. Chú ý ở Phiên bản kế tiếp
Hệ thống đã chuẩn bị sẵn cơ sở "mockup format" và logic trích xuất text JSON. Khi bạn import dữ liệu trên Notion, có thể Notion Object Properties (Rich text / Select / Number) của bạn có thiết lập Tên cột hơi khác với code mẫu.
-  **Cách fix đơn giản nhất**: Tạo cột trên Notion đúng với tên cột được Code gọi (VD: `Topic`, `Product ID`, `Content`, `Status`, `Customer Name`...).
-  **Lên phiên bản thật**: Nếu bạn gặp lỗi field names, xin thông báo lại màn hình log lỗi để tôi điều chỉnh giúp bạn `app/notion_db.py` là tương thích ngay.
