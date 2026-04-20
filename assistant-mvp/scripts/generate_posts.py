import os
import json
import uuid
import datetime
from pathlib import Path
from dotenv import load_dotenv
from app.utils import logger
from app.notion_db import fetch_products, insert_post
from app.claude_api import generate_text_claude

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = os.path.join(BASE_DIR, "prompts", "content_prompt.md")

def load_prompt_template() -> str:
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

def run_content_agent():
    logger.info("--- Starting Content Agent ---")
    products_db = os.getenv("NOTION_PRODUCTS_DB_ID")
    posts_db = os.getenv("NOTION_POSTS_DB_ID")
    
    if not products_db or not posts_db:
        logger.error("Missing NOTION_PRODUCTS_DB_ID or NOTION_POSTS_DB_ID in env.")
        return
        
    products = fetch_products(products_db)
    if not products:
        logger.info("No products found to generate contents.")
        return
        
    template = load_prompt_template()
    
    for prod in products:
        # Ở đây Product Notion return dạng JSON rườm rà. Code giả định format đơn giản
        props = prod.get("properties", {})
        
        # Helper lấy text từ rich_text Notion
        def get_text(prop_name: str, default: str = ""):
            try:
                if props[prop_name]["type"] == "title":
                    return props[prop_name]["title"][0]["plain_text"]
                return props[prop_name]["rich_text"][0]["plain_text"]
            except Exception:
                return default
                
        # Helper lấy số
        def get_number(prop_name: str, default=0):
            try:
                return props[prop_name]["number"]
            except:
                return default
                
        status = props.get("Status", {}).get("select", {}).get("name", "active")
        if status.lower() != "active":
            logger.info(f"Skipping product ID {prod['id']} due to inactive status.")
            continue
            
        name = get_text("Name", "Không tên")
        niche = get_text("Niche", "Bán lẻ / Dịch vụ")
        short_desc = get_text("Short Description")
        target_cust = get_text("Target Customer")
        pain = get_text("Pain Point")
        benefit = get_text("Benefit")
        price = get_number("Price", 0)
        cta = get_text("CTA")
        
        # Prepare Prompt
        prompt = template.format(
            num_posts=1,
            niche=niche,
            name=name,
            short_description=short_desc,
            target_customer=target_cust,
            pain_point=pain,
            benefit=benefit,
            price=price,
            cta=cta
        )
        
        logger.info(f"Generating posts for Product: {name}...")
        
        # Model call
        system_prompt = "You are a helpful AI Sales assistant that outputs strict JSON formats."
        response_json_str = generate_text_claude(prompt, system_prompt=system_prompt)
        
        if not response_json_str:
            continue
            
        try:
            clean_json_str = response_json_str.strip()
            if clean_json_str.startswith("```"):
                clean_json_str = clean_json_str.split("\n", 1)[-1]
            if clean_json_str.endswith("```"):
                clean_json_str = clean_json_str[:-3]
            clean_json_str = clean_json_str.strip()
            
            posts_data = json.loads(clean_json_str)
            if not isinstance(posts_data, list):
                # Fallback, có thể model trả về dict dạng {"posts": [...]}
                posts_data = posts_data.get("posts", posts_data)
                
            logger.info(f"Generated {len(posts_data)} posts. Uploading to Notion...")
            

            for idx, p in enumerate(posts_data):
                topic = p.get("topic", "No Topic")
                content = p.get("content", "No Content")
                
                # Split content into chunks of 2000 chars for Notion paragraph limits
                chunk_size = 2000
                children = []
                for i in range(0, len(content), chunk_size):
                    chunk = content[i:i+chunk_size]
                    children.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"text": {"content": chunk}}]
                        }
                    })
                
                # Insert vào Posts Notion
                unique_post_id = f"POST-{uuid.uuid4().hex[:8].upper()}"
                
                # Cố định mốc 9h sáng ngày mai (giờ server), cộng thêm idx để nếu có nhiều bài thì các bài cách nhau 1 tiếng
                tomorrow = datetime.datetime.now().astimezone() + datetime.timedelta(days=1)
                safe_hour = min(9 + idx*3, 23)
                scheduled_time_iso = tomorrow.replace(hour=safe_hour, minute=0, second=0, microsecond=0).isoformat()
                
                post_payload = {
                    "Post ID": {"rich_text": [{"text": {"content": unique_post_id}}]},
                    "Scheduled Date": {"date": {"start": scheduled_time_iso}},
                    "Name": {"title": [{ "text": { "content": topic } }]},
                    "Topic": {"rich_text": [{"text": {"content": topic}}]},
                    "Product ID": {"rich_text": [{"text": {"content": prod['id']}}]},
                    "Status": {"status": {"name": "Draft"}},
                    "Channel": {"select": {"name": "bluesky"}}
                }
                insert_post(posts_db, post_payload, children)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI JSON response: {e}\nRaw output: {response_json_str}")
        
    logger.info("--- Content Agent execution completed ---")

if __name__ == "__main__":
    run_content_agent()
