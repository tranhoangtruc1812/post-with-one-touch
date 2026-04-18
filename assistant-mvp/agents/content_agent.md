# Content Agent

## Đầu vào (Input)
- Đọc thông tin các sản phẩm từ bảng `Products` (Tên, Mô tả, Khách hàng mục tiêu, Nỗi đau (Pain point), Lợi ích, Giá, Lời kêu gọi hành động (CTA)).
- Chỉ lấy các sản phẩm có `status == "active"`.
- Số lượng bài cần sinh: 3-5 bài cho mỗi sản phẩm mỗi ngày (tuỳ cấu hình).

## Đầu ra (Output)
- Chuyển JSON Output từ AI Model thành các dòng Record và thêm vào bảng Notion `Posts`.
- Trạng thái mặc định: `status_draft = "draft"`, `approved = False`.

## Logic Flow
1. Scheduler gọi `scripts/generate_posts.py`.
2. Script đọc dữ liệu từ Notion.
3. Với mỗi sản phẩm, gộp Data vào file mẫu `prompts/content_prompt.md`.
4. Gọi OpenCode API (hoặc OpenAI endpoint tương thích) để yêu cầu AI sinh bài.
5. Parse JSON trả về, đảm bảo log lỗi nếu JSON lỗi (fallback logic nếu cần).
6. Gọi `insert_post` vào API Notion.
