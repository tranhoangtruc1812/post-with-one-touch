import os
from pathlib import Path
from dotenv import load_dotenv
from app.utils import logger
from app.claude_api import generate_text_claude
import requests
import datetime

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = os.path.join(BASE_DIR, "prompts", "report_prompt.md")

def load_prompt_template() -> str:
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

def run_report_agent():
    logger.info("--- Starting Daily Report Agent ---")
    headers = {
        "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    posts_db = os.getenv("NOTION_POSTS_DB_ID")
    
    if not posts_db:
        logger.error("Missing NOTION_POSTS_DB_ID env variable.")
        return
        
    try:
        # Trong hệ thống thực, sẽ cần thêm query bounds (date = today),
        # Tại mockup này, script đọc Count raw length.
        logger.info("Đang query dữ liệu Notion...")
        res_posts = requests.post(f"https://api.notion.com/v1/databases/{posts_db}/query", headers=headers, json={})
        posts = res_posts.json().get('results', [])
        
        drafts = 0
        published = 0
        channels_count = {}
        failed_posts = []
        now = datetime.datetime.now(datetime.timezone.utc)
        
        for p in posts:
            props = p.get("properties", {})
            status = props.get("Status", {}).get("status", {}).get("name") or props.get("Status", {}).get("select", {}).get("name") or "Unknown"
            
            if status == "Draft":
                drafts += 1
            elif status == "Published":
                published += 1
                
            channel = props.get("Channel", {}).get("select", {}).get("name") or "Unknown Channel"
            channels_count[channel] = channels_count.get(channel, 0) + 1
            
            if status == "Approved" and "Scheduled Date" in props and props["Scheduled Date"]["type"] == "date" and props["Scheduled Date"]["date"]:
                scheduled_date_str = props["Scheduled Date"]["date"]["start"]
                try:
                    scheduled_time = datetime.datetime.fromisoformat(scheduled_date_str.replace('Z', '+00:00'))
                    if scheduled_time < now:
                        topic_raw = props.get("Topic", {}).get("rich_text", [])
                        topic = "".join([t["plain_text"] for t in topic_raw]) if topic_raw else "Không có chủ đề"
                        time_only = scheduled_date_str.split("T")[1][:5] if "T" in scheduled_date_str else scheduled_date_str
                        failed_posts.append(f"⚠️ {time_only} | Chủ đề: {topic}")
                except Exception:
                    pass
                    
        failed_posts_str = "\n".join(failed_posts) if failed_posts else "✅ Không có bài nào bị lỗi."
        channel_stats_str = "\n".join([f"  + Kênh {ch}: {cnt} bài" for ch, cnt in channels_count.items()])
        
        # Lọc các bài đăng có lịch trong ngày hôm nay
        today_date_str = datetime.datetime.now().astimezone().strftime('%Y-%m-%d')
        today_scheduled_posts = []
        for p in posts:
            props = p.get("properties", {})
            if "Scheduled Date" in props and props["Scheduled Date"]["type"] == "date" and props["Scheduled Date"]["date"]:
                scheduled_date_full = props["Scheduled Date"]["date"]["start"]
                if scheduled_date_full.startswith(today_date_str):
                    topic_raw = props.get("Topic", {}).get("rich_text", [])
                    topic = "".join([t["plain_text"] for t in topic_raw]) if topic_raw else "Không có chủ đề"
                    status = props.get("Status", {}).get("status", {}).get("name") or props.get("Status", {}).get("select", {}).get("name") or "Unknown"
                    time_only = scheduled_date_full.split("T")[1][:5] if "T" in scheduled_date_full else "Tự do"
                    today_scheduled_posts.append(f"⏰ *{time_only}* | Trạng thái: {status}\n📌 Chủ đề: {topic}")
        
        if not today_scheduled_posts:
            scheduled_posts_table = "Không có bài viết nào được lên lịch cho hôm nay."
        else:
            scheduled_posts_table = "\n\n".join(today_scheduled_posts)
        
        # Tạo prompt
        prompt = load_prompt_template().format(
            draft_count=drafts,
            published_count=published,
            scheduled_posts_table=scheduled_posts_table,
            channel_stats=channel_stats_str,
            failed_posts=failed_posts_str
        )
        
        # Call model. (Báo cáo cần Text, không force JSON)
        # Note: Hàm generate_text_claude đang force json_object. 
        # Để chạy tốt, ta có thể tạm override.
        system_prompt = "You are an intelligent reporter. Output standard plain text."
        report_text = generate_text_claude(prompt, system_prompt)
        
        # Bóc tách nếu nó lỡ trả JSON format
        if "{" in report_text and "}" in report_text:
             report_text = f"Report Data: \n{report_text}"
             
        logger.info("\n==============================\n")
        logger.info(f"BÁO CÁO CUỐI NGÀY:\n{report_text}\n")
        logger.info("==============================\n")

        # Gửi sang Telegram
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if telegram_token and telegram_chat_id:
            try:
                tel_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                payload = {
                    "chat_id": telegram_chat_id,
                    "text": f"📊 *BÁO CÁO DAILY MỚI NHẤT*\n\n{report_text}",
                    "parse_mode": "Markdown"
                }
                res = requests.post(tel_url, json=payload, timeout=10)
                res.raise_for_status()
                logger.info("Đã gửi báo cáo qua Telegram thành công!")
            except Exception as e:
                logger.error(f"Lỗi gửi tin nhắn báo cáo qua Telegram: {e}")

    except Exception as e:
        logger.error(f"Generate Report Failed: {e}")

if __name__ == "__main__":
    run_report_agent()
