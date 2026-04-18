import os
import requests
from urllib.parse import quote
from pathlib import Path
from dotenv import load_dotenv
from app.utils import logger
from app.claude_api import generate_text_claude

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = os.path.join(BASE_DIR, "prompts", "image_prompt.md")


def load_prompt_template() -> str:
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def generate_image_url(prompt: str, width: int = 1024, height: int = 1024) -> str:
    """
    Tạo URL ảnh từ Pollinations.ai (miễn phí, không cần API key).
    URL trả về chính là link ảnh vĩnh viễn.
    """
    encoded_prompt = quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"

    # Verify URL hoạt động bằng HEAD request
    try:
        response = requests.head(image_url, timeout=60, allow_redirects=True)
        if response.status_code == 200:
            logger.info(f"Generated image URL: {image_url[:100]}...")
            return image_url
        else:
            logger.error(f"Pollinations URL trả về status {response.status_code}")
            return ""
    except Exception as e:
        logger.error(f"Lỗi kiểm tra Pollinations URL: {e}")
        return ""


def update_post_image_prompt(post_id: str, image_prompt: str):
    """Cập nhật Image_Prompt lên Notion database"""
    notion_url = f"https://api.notion.com/v1/pages/{post_id}"
    headers = {
        "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    payload = {
        "properties": {
            "Image_Prompt": {"rich_text": [{"text": {"content": image_prompt[:2000]}}]}
        }
    }
    try:
        response = requests.patch(notion_url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info(f"Đã cập nhật Image_Prompt cho post {post_id}.")
    except Exception as e:
        logger.error(f"Lỗi cập nhật Image_Prompt lên Notion: {e}")


def update_post_image_url(post_id: str, image_url: str):
    """Cập nhật Image_URL lên Notion database"""
    notion_url = f"https://api.notion.com/v1/pages/{post_id}"
    headers = {
        "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    payload = {
        "properties": {
            "Image_URL": {"url": image_url}
        }
    }
    try:
        response = requests.patch(notion_url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info(f"Đã cập nhật Image_URL cho post {post_id}.")
    except Exception as e:
        logger.error(f"Lỗi cập nhật Image_URL lên Notion: {e}")


def run_image_agent():
    logger.info("--- Starting Image Generation Agent ---")
    posts_db = os.getenv("NOTION_POSTS_DB_ID")
    if not posts_db:
        logger.error("Missing NOTION_POSTS_DB_ID in env.")
        return

    # Lấy các bài Draft mà chưa có Image_URL
    url = f"https://api.notion.com/v1/databases/{posts_db}/query"
    headers = {
        "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    payload = {
        "filter": {
            "and": [
                {
                    "property": "Status",
                    "status": {"equals": "Draft"}
                },
                {
                    "property": "Image_URL",
                    "url": {"is_empty": True}
                }
            ]
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        results = response.json().get("results", [])
        logger.info(f"Tìm thấy {len(results)} bài cần tạo Image.")

        template = load_prompt_template()

        for post in results:
            post_id = post["id"]
            props = post["properties"]

            # Lấy content
            content_chunks = props.get("Content", {}).get("rich_text", [])
            content = "".join([c["plain_text"] for c in content_chunks]) if content_chunks else ""

            # Lấy chủ đề
            topic_chunks = props.get("Topic", {}).get("title", [])
            topic = "".join([c["plain_text"] for c in topic_chunks]) if topic_chunks else "No Topic"

            channel = "Facebook"
            if "Kênh" in props and props["Kênh"].get("select"):
                channel = props["Kênh"]["select"]["name"]

            target_audience = "Người tiêu dùng trực tuyến"
            post_brief = f"Chủ đề: {topic}\nNội dung: {content}"

            # --- Bước 1: Sinh image prompt bằng Claude/OpenRouter LLM ---
            logger.info(f"[1/2] Generating image prompt for Post {post_id}...")
            llm_prompt = template.format(
                post_content=post_brief,
                channel=channel,
                target_audience=target_audience
            )
            system_prompt = "You are a creative prompt engineer. Output only the prompt text in English. Do not explain."

            image_prompt_text = generate_text_claude(llm_prompt, system_prompt=system_prompt)
            if not image_prompt_text:
                logger.warning(f"Không sinh được image prompt cho post {post_id}, bỏ qua.")
                continue

            image_prompt_text = image_prompt_text.strip()
            logger.info(f"Generated Image Prompt:\n{image_prompt_text}")

            # Lưu image prompt vào Notion
            update_post_image_prompt(post_id, image_prompt_text)

            # --- Bước 2: Tạo URL ảnh từ Pollinations.ai & lưu vào Notion ---
            logger.info(f"[2/2] Generating image URL for Post {post_id}...")
            image_url = generate_image_url(image_prompt_text)
            if not image_url:
                logger.warning(f"Không tạo được URL ảnh cho post {post_id}, bỏ qua.")
                continue

            update_post_image_url(post_id, image_url)
            logger.info(f"✅ Hoàn tất: Post {post_id} → {image_url[:80]}...")

    except Exception as e:
        logger.error(f"Lỗi truy vấn posts để generate image: {e}")

    logger.info("--- Image Generation Agent execution completed ---")

if __name__ == "__main__":
    run_image_agent()
