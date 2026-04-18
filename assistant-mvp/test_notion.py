import os
import requests
from dotenv import load_dotenv

load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
posts_db = os.getenv("NOTION_POSTS_DB_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28"
}

url = f"https://api.notion.com/v1/databases/{posts_db}"
response = requests.get(url, headers=HEADERS)
import json
with open("posts_db_schema.json", "w", encoding='utf-8') as f:
    json.dump(response.json(), f, indent=2)
