import os
import requests
from dotenv import load_dotenv
from app.utils import logger

load_dotenv()

OPENCODE_API_KEY = os.getenv("OPENCODE_API_KEY")
OPENCODE_API_URL = os.getenv("OPENCODE_API_URL", "https://api.opencode.vn/v1/chat/completions")

def generate_text_opencode(prompt: str, system_prompt: str = "") -> str:
    """
    Gửi request lên OpenCode API (chuẩn OpenAI Chat Completions endpoint).
    """
    headers = {
        "Authorization": f"Bearer {OPENCODE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": "opencode-latest", # Thay đổi theo cấu hình của loại model OpenCode
        "messages": messages,
        "temperature": 0.7,
        "response_format": {"type": "json_object"} # Nỗ lực force JSON nếu model hỗ trợ
    }
    
    try:
        response = requests.post(OPENCODE_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        # Trích xuất nội dung
        content = data['choices'][0]['message']['content']
        return content
    except Exception as e:
        logger.error(f"Error calling OpenCode API: {e}")
        return ""
