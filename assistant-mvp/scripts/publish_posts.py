import os
import datetime
from dotenv import load_dotenv
from app.utils import logger
import requests 

load_dotenv()

def publish_to_channel(channel: str, content: str) -> str:
    """
    Giả lập đăng bài lên test platform.
    Trong thực tế bản v2, có thể tích hợp Facebook Graph API.
    """
    logger.info(f"[PUBLISH AGENT] Đang thực thi đăng bài lên nền tảng {channel}...")
    logger.info(f"Nội dung Demo:\n{content[:80]}...\n{'='*30}")
    
    # Mock URL trả về từ nền tảng
    mock_url = f"https://{channel.lower()}.com/mock_post_{int(datetime.datetime.now().timestamp())}"
    return mock_url

def mark_post_as_published(post_id: str, url: str):
    """
    Cập nhật trạng thái bài viết trên Notion
    """
    notion_url = f"https://api.notion.com/v1/pages/{post_id}"
    headers = {
        "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    payload = {
        "properties": {
            "Status": {"status": {"name": "Published"}},
        }
    }
    try:
        response = requests.patch(notion_url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info(f"Đã cập nhật Notion post {post_id} thành Published.")
    except Exception as e:
        logger.error(f"Lỗi cập nhật publish status trên Notion: {e}")

def run_publish_agent():
    logger.info("--- Starting Publish Agent ---")
    posts_db = os.getenv("NOTION_POSTS_DB_ID")
    if not posts_db:
        logger.error("Missing NOTION_POSTS_DB_ID in env. Bỏ qua...")
        return
        
    url = f"https://api.notion.com/v1/databases/{posts_db}/query"
    headers = {
        "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Lọc bài Draft + Approved = True
    payload = {
        "filter": {
            "and": [
                {
                    "property": "Status",
                    "status": {"equals": "Draft"}
                },
                {
                    "property": "Approved",
                    "checkbox": {"equals": True}
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        results = response.json().get("results", [])
        
        logger.info(f"Summary: Tìn thấy {len(results)} bài thỏa mãn điều kiện đăng tải tức thì.")
        
        for post in results:
            post_id = post["id"]
            props = post["properties"]
            
            # Lấy content
            content_chunks = props.get("Content", {}).get("rich_text", [])
            content = "".join([c["plain_text"] for c in content_chunks]) if content_chunks else ""
            
            # Lấy channel mạng xã hội
            channel = "Facebook"
            if "Channel" in props and props["Channel"].get("select"):
                channel = props["Channel"]["select"]["name"]
            
            if content:
                # 1. Đăng lên Mạng xã hội
                post_url = publish_to_channel(channel, content)
                # 2. Cập nhật URL và Trạng thái về Database
                mark_post_as_published(post_id, post_url)
            else:
                logger.warning(f"Post {post_id} rỗng. Bỏ qua.")
                
    except Exception as e:
        logger.error(f"Lỗi truy vấn posts để publish: {e}")
        
    logger.info("--- Publish Agent execution completed ---")

if __name__ == "__main__":
    run_publish_agent()
