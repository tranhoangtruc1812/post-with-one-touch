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
    orders_db = os.getenv("NOTION_ORDERS_DB_ID")
    
    if not posts_db or not orders_db:
        logger.error("Missing Notion DB env variables.")
        return
        
    try:
        # Trong hệ thống thực, sẽ cần thêm query bounds (date = today),
        # Tại mockup này, script đọc Count raw length.
        logger.info("Đang query dữ liệu Notion...")
        res_posts = requests.post(f"https://api.notion.com/v1/databases/{posts_db}/query", headers=headers, json={})
        posts = res_posts.json().get('results', [])
        
        res_orders = requests.post(f"https://api.notion.com/v1/databases/{orders_db}/query", headers=headers, json={})
        orders = res_orders.json().get('results', [])
        
        drafts = len([p for p in posts if p.get("properties", {}).get("Status", {}).get("select", {}).get("name") == "Draft"])
        published = len([p for p in posts if p.get("properties", {}).get("Status", {}).get("select", {}).get("name") == "Published"])
        total_orders = len(orders)
        
        # Tạo prompt
        prompt = load_prompt_template().format(
            draft_count=drafts,
            published_count=published,
            order_count=total_orders
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

    except Exception as e:
        logger.error(f"Generate Report Failed: {e}")

if __name__ == "__main__":
    run_report_agent()
