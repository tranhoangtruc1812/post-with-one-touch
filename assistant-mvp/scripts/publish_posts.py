import os
import datetime
from dotenv import load_dotenv
from app.utils import logger
import requests 
from atproto import Client
from scripts.check_reviews import get_post_content_from_blocks

load_dotenv()

def publish_to_channel(channel: str, content: str) -> str:
    """
    Giả lập đăng bài lên test platform.
    Trong thực tế bản v2, có thể tích hợp Facebook Graph API.
    Có tích hợp đăng thật lên Bluesky nếu channel là Bluesky.
    """
    logger.info(f"[PUBLISH AGENT] Đang thực thi đăng bài lên nền tảng {channel}...")
    logger.info(f"Nội dung Demo:\n{content[:80]}...\n{'='*30}")

    post_result = {
        "success": False,
        "url": "",
        "message": ""
    }
    
    if channel.lower() == "bluesky":
        try:
            bsky_handle = os.getenv("BLUESKY_HANDLE")
            bsky_password = os.getenv("BLUESKY_PASSWORD")
            
            if not bsky_handle or not bsky_password:
                logger.error("Thiếu cấu hình BLUESKY_HANDLE hoặc BLUESKY_PASSWORD trong env.")
                return f"https://bsky.app/profile/error"
                
            client = Client()
            client.login(bsky_handle, bsky_password)

            with open('../image.jpg', 'rb') as f:
                img_data = f.read()
            
            if len(content) > 300:
                content = content[:297] + "..."
            # Đăng bài
            post = client.send_image(
                text=content,
                image=img_data,
                image_alt=''
            )
            
            # Tạo URL của bài viết
            post_uri = post.uri
            parts = post_uri.split('/')
            rkey = parts[-1]
            did = parts[-3]
            post_url = f"https://bsky.app/profile/{did}/post/{rkey}"
            
            logger.info(f"Đăng bài thành công lên Bluesky: {post_url}")
            post_result["success"] = True
            post_result["url"] = post_url
            post_result["message"] = "Đăng bài thành công lên Bluesky"
            return post_result
            
        except Exception as e:
            logger.error(f"Lỗi khi đăng lên Bluesky: {e}")
            post_result["success"] = False
            post_result["url"] = "https://bsky.app/profile/error"
            post_result["message"] = f"Lỗi khi đăng lên Bluesky: {e}"
            return post_result
            
    # Mock URL trả về từ nền tảng khác
    mock_url = f"https://{channel.lower()}.com/mock_post_{int(datetime.datetime.now().timestamp())}"
    post_result["success"] = True
    post_result["url"] = mock_url
    post_result["message"] = f"Đăng bài thành công lên {channel}"
    return post_result

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
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    payload = {
        "properties": {
            "Status": {"status": {"name": "Published"}},
            "Published Date": {"date": {"start": now_iso}}
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
                    "status": {"equals": "Approved"}
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
            
            # Kiểm tra thời gian hẹn đăng (Scheduled Date)
            if "Scheduled Date" in props and props["Scheduled Date"]["type"] == "date" and props["Scheduled Date"]["date"]:
                scheduled_date_str = props["Scheduled Date"]["date"]["start"]
                try:
                    scheduled_time = datetime.datetime.fromisoformat(scheduled_date_str.replace('Z', '+00:00'))
                    now = datetime.datetime.now(datetime.timezone.utc)
                    if scheduled_time > now:
                        logger.info(f"Post {post_id} chưa đến giờ đăng ({scheduled_date_str}). Bỏ qua.")
                        continue
                except Exception as e:
                    logger.warning(f"Lỗi parse Scheduled Date cho post {post_id}: {e}")
            
            # Lấy content
            content = get_post_content_from_blocks(post_id)
            if not content or not content.strip():
                content = ""
            
            # Lấy channel mạng xã hội
            channel = "bluesky"
            if "Channel" in props and props["Channel"].get("select"):
                channel = props["Channel"]["select"]["name"]
            
            if content:
                # 1. Đăng lên Mạng xã hội
                post_result = publish_to_channel(channel, content)
                # 2. Cập nhật URL và Trạng thái về Database
                if(post_result["success"]):
                    mark_post_as_published(post_id, post_result["url"])
            else:
                logger.warning(f"Post {post_id} rỗng. Bỏ qua.")
                
    except Exception as e:
        logger.error(f"Lỗi truy vấn posts để publish: {e}")
        
    logger.info("--- Publish Agent execution completed ---")

if __name__ == "__main__":
    run_publish_agent()
