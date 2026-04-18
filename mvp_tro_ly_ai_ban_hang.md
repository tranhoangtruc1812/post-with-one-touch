# MVP trợ lý AI bán hàng

## Mục tiêu
Tạo một trợ lý AI hỗ trợ 3 việc cốt lõi:
1. Viết content mỗi ngày
2. Hỗ trợ đăng bài theo lịch
3. Quản lý đơn hàng cơ bản

MVP này ưu tiên:
- dễ làm trong 7–14 ngày
- chi phí thấp
- có thể chạy thật
- có thể nâng cấp dần thành hệ thống 24/7

---

## Kết quả mong muốn sau MVP
Sau khi hoàn thành, hệ thống phải làm được:
- nhập thông tin sản phẩm một lần
- AI tự sinh 3–5 bài viết theo style cố định
- lưu bài vào nơi để duyệt
- khi bài được duyệt, hệ thống đưa sang kênh đăng
- gom đơn hàng về một nơi
- AI tự phân loại đơn và gợi ý phản hồi
- cuối ngày có báo cáo ngắn

---

## Phạm vi MVP
### Có trong MVP
- Content assistant
- Publish assistant bán tự động
- Order assistant mức cơ bản
- Báo cáo cuối ngày

### Chưa làm ở MVP
- Tự động chốt sale hoàn toàn
- CRM đầy đủ
- Dashboard phức tạp
- Tự động đăng đa nền tảng mức cao
- AI chatbot nói chuyện tự do với khách hàng ở mọi kênh

---

## Kiến trúc tổng thể

### 1. Bộ não điều phối
OpenCode hoặc một agent runner tương đương

Nhiệm vụ:
- đọc dữ liệu sản phẩm
- sinh bài viết
- chọn CTA
- gọi script đăng bài
- gọi script xử lý đơn
- tạo báo cáo cuối ngày

### 2. Nguồn dữ liệu
Google Sheets hoặc Airtable

Tạo 3 bảng:
- products
- posts
- orders

### 3. Script thực thi
Các script nhỏ:
- generate_posts.py
- publish_posts.py
- sync_orders.py
- reply_suggestions.py
- daily_report.py

### 4. Lịch chạy
- cron hoặc APScheduler
- chạy định kỳ theo giờ

---

## Thiết kế dữ liệu

### Bảng products
- product_id
- name
- short_description
- target_customer
- pain_point
- benefit
- price
- cta
- status

### Bảng posts
- post_id
- product_id
- topic
- channel
- content
- status_draft
- approved
- scheduled_time
- posted_time
- post_url

### Bảng orders
- order_id
- created_time
- customer_name
- phone
- source
- product_name
- amount
- payment_status
- order_status
- priority
- note
- ai_reply_suggestion

---

## 4 agent trong MVP

### 1. Content Agent
Input:
- thông tin sản phẩm
- insight khách hàng
- style viết

Output:
- 3–5 bài viết/ngày

Format chuẩn:
- hook
- pain
- solution
- CTA

### 2. Publish Agent
Input:
- bài đã approved
- kênh đăng
- thời gian đăng

Output:
- trạng thái posted
- link bài đăng
- log lỗi nếu có

### 3. Order Agent
Input:
- đơn mới

Output:
- gán trạng thái
- gợi ý phản hồi
- gắn mức ưu tiên

### 4. Report Agent
Input:
- dữ liệu bài viết + đơn hàng trong ngày

Output:
- báo cáo cuối ngày

---

## Flow vận hành

### Flow 1: Tạo content
1. Bạn nhập sản phẩm vào products
2. Scheduler gọi Content Agent
3. Agent sinh 3–5 bài
4. Ghi vào posts với trạng thái draft
5. Bạn duyệt nhanh

### Flow 2: Đăng bài
1. Publish Agent đọc các bài approved
2. Gọi script publish
3. Cập nhật posted_time và post_url
4. Ghi log nếu thất bại

### Flow 3: Quản lý đơn
1. Đơn mới vào orders từ form hoặc nhập tay
2. Order Agent đọc đơn mới
3. Tự gán trạng thái
4. Sinh gợi ý phản hồi
5. Đánh dấu đơn cần xử lý tay nếu thiếu dữ liệu

### Flow 4: Báo cáo cuối ngày
1. Scheduler chạy 20:30
2. Report Agent tổng hợp
3. Tạo báo cáo ngắn gồm:
   - số bài đã tạo
   - số bài đã đăng
   - số đơn mới
   - số đơn tồn
   - vấn đề phát sinh

---

## Stack đề xuất

### Bản đơn giản nhất
- OpenCode
- Python
- Google Sheets
- Telegram bot hoặc web form
- APScheduler hoặc cron
- 1 VPS nhỏ

### Vì sao chọn stack này
- rẻ
- nhanh dựng
- dễ sửa
- dễ chuyển sang bản lớn hơn

---

## Cấu trúc thư mục gợi ý

```text
assistant-mvp/
├─ AGENTS.md
├─ opencode.json
├─ .env
├─ app/
│  ├─ main.py
│  ├─ scheduler.py
│  ├─ sheets.py
│  ├─ models.py
│  └─ utils.py
├─ agents/
│  ├─ content_agent.md
│  ├─ publish_agent.md
│  ├─ order_agent.md
│  └─ report_agent.md
├─ scripts/
│  ├─ generate_posts.py
│  ├─ publish_posts.py
│  ├─ sync_orders.py
│  ├─ reply_suggestions.py
│  └─ daily_report.py
└─ prompts/
   ├─ content_prompt.md
   ├─ order_prompt.md
   └─ report_prompt.md
```

---

## Luật viết cho Content Agent
- chỉ viết trong 1 niche duy nhất
- tiếng Việt tự nhiên
- không nói quá lố
- luôn có hook đầu bài
- luôn có CTA cuối
- dùng trải nghiệm thật, pain thật, ngôn ngữ dễ hiểu
- một bài chỉ tập trung vào một ý chính

---

## Luật xử lý đơn
- nếu thiếu số điện thoại hoặc sản phẩm: gắn need_manual_check
- nếu đơn mới: gắn new
- nếu đã có xác nhận thanh toán: gắn paid
- nếu quá 24h chưa xử lý: gắn high_priority

---

## Lịch chạy đề xuất
- 08:00: generate_posts
- 11:30: check approved posts
- 15:00: check approved posts
- mỗi 10 phút: sync_orders
- 20:30: daily_report

---

## Chỉ số thành công của MVP
- tạo được ít nhất 3 bài/ngày
- mỗi bài duyệt trong dưới 2 phút
- mọi đơn được gom về 1 nơi
- 80% đơn có gợi ý phản hồi tự động
- báo cáo cuối ngày chạy ổn định

---

## Rủi ro cần tránh
- cố tự động hóa quá nhiều ngay từ đầu
- dùng quá nhiều công cụ
- đổi style content liên tục
- không có trạng thái lỗi và log
- để AI tự đăng mọi thứ mà không có bước duyệt

---

## Phiên bản nâng cấp sau MVP
- thêm chatbot Telegram nhận lead
- thêm auto reply theo kịch bản
- chuyển từ Google Sheets sang PostgreSQL
- thêm dashboard admin
- thêm scoring khách hàng tiềm năng
- thêm nhiều kênh đăng bài

---

## Kế hoạch triển khai 7 ngày

### Ngày 1
- dựng project
- tạo sheets
- chuẩn hóa dữ liệu

### Ngày 2
- làm Content Agent
- test sinh 3 bài từ 1 sản phẩm

### Ngày 3
- lưu bài vào bảng posts
- thêm cột approved

### Ngày 4
- làm Publish Agent cho 1 kênh đơn giản

### Ngày 5
- làm Order Agent
- test phân loại đơn

### Ngày 6
- thêm scheduler
- thêm log

### Ngày 7
- làm daily report
- test end-to-end

---

## Bản chốt cho MVP đầu tiên
MVP đầu tiên nên là:
- 1 niche duy nhất
- 1 kênh đăng chính
- 1 nguồn nhận đơn
- 1 bảng dữ liệu trung tâm
- 4 agent đơn giản

Đây là bản đủ nhỏ để làm xong, nhưng đủ thật để bắt đầu tạo ra kết quả.

