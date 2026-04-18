import os
import json
from pathlib import Path
from dotenv import load_dotenv
from app.utils import logger
from app.claude_api import generate_text_claude
import requests

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = os.path.join(BASE_DIR, "prompts", "order_prompt.md")

def load_prompt_template() -> str:
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

def run_order_agent():
    logger.info("--- Starting Order Agent (Reply Suggestions) ---")
    orders_db = os.getenv("NOTION_ORDERS_DB_ID")
    
    if not orders_db:
        logger.error("Missing NOTION_ORDERS_DB_ID in env.")
        return
        
    url = f"https://api.notion.com/v1/databases/{orders_db}/query"
    headers = {
        "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Fetch NEW orders
    payload = {
        "filter": {
            "property": "Status",
            "status": {"equals": "New"}
        }
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()
        orders = res.json().get("results", [])
        
        logger.info(f"Phát hiện {len(orders)} đơn hàng mới cần xử lý.")
        
        template = load_prompt_template()
        
        for order in orders:
            order_id = order["id"]
            props = order["properties"]
            
            # Helper extracts text
            def get_text(prop_col, default=""):
                try:
                    if props[prop_col]["type"] == "title":
                        return props[prop_col]["title"][0]["plain_text"]
                    return props[prop_col]["rich_text"][0]["plain_text"]
                except:
                    return default
            
            def get_number(prop_col, default=0):
                try:
                    return props[prop_col]["number"]
                except:
                    return default
                    
            customer_name = get_text("Customer Name", "Khách hàng")
            phone = get_text("Phone", "Chưa có")
            product_name = get_text("Product Name", "Không rõ sản phẩm")
            note = get_text("Note", "Không có ghi chú")
            amount = get_number("Amount", 0)
            
            # Xây dựng prompt
            prompt = template.format(
                customer_name=customer_name,
                phone=phone,
                product_name=product_name,
                note=note,
                amount=amount
            )
            
            system_prompt = "You are an AI Sales Assistant. Always respond with strict JSON."
            response_json_str = generate_text_claude(prompt, system_prompt)
            
            if not response_json_str:
                logger.warning(f"Order {order_id} failed to get AI response.")
                continue
                
            try:
                ai_data = json.loads(response_json_str)
                priority = ai_data.get("priority", "normal")
                tag = ai_data.get("tag", "valid")
                ai_reply = ai_data.get("ai_reply_suggestion", "")
                
                # Cập nhật Notion Record qua Patch API
                patch_url = f"https://api.notion.com/v1/pages/{order_id}"
                update_payload = {
                    "properties": {
                        "Priority": {"select": {"name": priority.capitalize()}},
                        "Tag": {"select": {"name": tag}},
                        "AI Reply": {"rich_text": [{"text": {"content": ai_reply[:2000]}}]},
                        "Status": {"select": {"name": "Processing"}} # Đổi status để ko bị pick lại
                    }
                }
                
                requests.patch(patch_url, headers=headers, json=update_payload)
                logger.info(f"Đã xử lý Order {order_id} - Reply Length: {len(ai_reply)}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Order AI JSON: {e}")
                
    except Exception as e:
        logger.error(f"Lỗi truy vấn Database Orders: {e}")
        
    logger.info("--- Order Agent execution completed ---")

if __name__ == "__main__":
    run_order_agent()
