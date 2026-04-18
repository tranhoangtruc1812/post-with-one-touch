import os
import requests
from dotenv import load_dotenv
from app.utils import logger

load_dotenv()

def get_posts_ready_for_review():
    """
    Query Notion for Posts with Status = 'Ready for Review'
    """
    posts_db = os.getenv("NOTION_POSTS_DB_ID")
    if not posts_db:
        logger.error("Missing NOTION_POSTS_DB_ID in env.")
        return []

    url = f"https://api.notion.com/v1/databases/{posts_db}/query"
    headers = {
        "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    payload = {
        "filter": {
            "property": "Status",
            "status": {"equals": "Ready for Review"}
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        results = response.json().get("results", [])
        return results
    except Exception as e:
        logger.error(f"Error querying Notion for review posts: {e}")
        return []

def get_post_content_from_blocks(post_id: str) -> str:
    """
    Lấy nội dung chi tiết bài viết từ các block con (children) của trang.
    """
    url = f"https://api.notion.com/v1/blocks/{post_id}/children"
    headers = {
        "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
        "Notion-Version": "2022-06-28"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        blocks = response.json().get("results", [])
        
        content_lines = []
        for block in blocks:
            block_type = block.get("type", "")
            if block_type and block_type in block:
                rich_text = block[block_type].get("rich_text", [])
                if rich_text:
                    line_text = "".join([t.get("plain_text", "") for t in rich_text])
                    if line_text:
                        content_lines.append(line_text)
                        
        return "\n\n".join(content_lines)
    except Exception as e:
        logger.error(f"Error fetching blocks for post {post_id}: {e}")
        return ""

def update_post_status(post_id: str, new_status: str) -> bool:
    """
    Cập nhật Status của post trên Notion
    """
    notion_url = f"https://api.notion.com/v1/pages/{post_id}"
    headers = {
        "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    payload = {
        "properties": {
            "Status": {"status": {"name": new_status}}
        }
    }
    try:
        response = requests.patch(notion_url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info(f"Đã cập nhật Notion post {post_id} thành {new_status}.")
        return True
    except Exception as e:
        logger.error(f"Lỗi cập nhật status trên Notion: {e}")
        return False


if __name__ == "__main__":
    get_post_content_from_blocks("34581d09-f2d7-814d-b163-c16b887155f5")
