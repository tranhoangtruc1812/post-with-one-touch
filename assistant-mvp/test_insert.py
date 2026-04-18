import os
from dotenv import load_dotenv
from app.notion_db import insert_post

load_dotenv()
posts_db = os.getenv("NOTION_POSTS_DB_ID")

post_payload = {
    "Topic": {"title": [{"text": {"content": "Test Topic With Paragraphs"}}]},
    "Product ID": {"rich_text": [{"text": {"content": "Test ID"}}]},
    "Status": {"status": {"name": "Draft"}},
    "Approved": {"checkbox": False}
}

children = [
    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"text": {"content": "First paragraph content."}}]
        }
    },
    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"text": {"content": "Second paragraph content."}}]
        }
    }
]

print("Inserting post with children...")
result = insert_post(posts_db, post_payload, children)
print("Result:", result)
