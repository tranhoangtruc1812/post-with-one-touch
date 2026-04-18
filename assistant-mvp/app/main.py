import os
from dotenv import load_dotenv
from app.utils import logger
from app.notion_db import fetch_products

from app.scheduler import start_scheduler

# Load environment variables
load_dotenv()

def main():
    logger.info("Starting AI Sales Assistant MVP...")
    
    # Test connection
    products_db = os.getenv("NOTION_PRODUCTS_DB_ID")
    if products_db:
        logger.info("Vui lòng đảm bảo bạn đã cung cấp Notion ID và API Key hợp lệ.")
    else:
        logger.warning("No NOTION_PRODUCTS_DB_ID configured. Check your .env file.")
        
    logger.info("Bắt đầu kích hoạt hệ thống tự động (Trợ lý AI bán hàng)...")
    start_scheduler()

if __name__ == "__main__":
    main()
