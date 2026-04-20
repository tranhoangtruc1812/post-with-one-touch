import os
import requests
import time
from dotenv import load_dotenv
from app.utils import logger

load_dotenv()

# Provider: "claude" (direct Anthropic) hoặc "openrouter"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "claude")

# Claude direct config
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")

# OpenRouter config
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4-20250514")


def _call_claude_direct(messages: list, system_prompt: str, model: str) -> str:
    """Gọi trực tiếp Anthropic Claude Messages API."""
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "max_tokens": 4096,
        "messages": messages,
        "temperature": 0.7,
    }

    if system_prompt:
        payload["system"] = system_prompt

    response = requests.post(
        "https://openrouter.ai/api/v1/messages",
        headers=headers,
        json=payload,
        timeout=60
    )
    response.raise_for_status()
    data = response.json()
    return data['content'][0]['text']


def _call_openrouter(messages: list, system_prompt: str, model: str) -> str:
    """Gọi qua OpenRouter API (chuẩn OpenAI-compatible)."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://assistant-mvp.local",
    }

    all_messages = []
    if system_prompt:
        all_messages.append({"role": "system", "content": system_prompt})
    all_messages.extend(messages)

    payload = {
        "model": model,
        "messages": all_messages,
        "max_tokens": 4096,
        "temperature": 0.7,
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )
    response.raise_for_status()
    data = response.json()
    return data['choices'][0]['message']['content']


def generate_text_claude(prompt: str, system_prompt: str = "") -> str:
    """
    Gửi request lên LLM provider (Claude direct hoặc OpenRouter).
    Chọn provider qua biến LLM_PROVIDER trong .env.
    Có cơ chế tự động retry 3 lần nếu có lỗi.
    """
    messages = [{"role": "user", "content": prompt}]
    max_retries = 3
    base_delay = 5 # seconds

    for attempt in range(max_retries):
        try:
            if LLM_PROVIDER == "openrouter":
                return _call_openrouter(messages, system_prompt, OPENROUTER_MODEL)
            else:
                return _call_claude_direct(messages, system_prompt, CLAUDE_MODEL)
        except Exception as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Error calling {LLM_PROVIDER} API: {e}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
            else:
                logger.error(f"Error calling {LLM_PROVIDER} API after {max_retries} attempts: {e}")
                return ""
