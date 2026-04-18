import os
import requests
from dotenv import load_dotenv
from app.utils import logger

load_dotenv()

def sync_orders():
    """
    Script để đồng bộ/lấy đơn từ các nguồn Form/POS (như Ladipage, WooCommerce webhook, TiktokShop) về Notion Orders Database.
    Trong tài liệu MVP, chúng ta coi đây là tính năng Standby, giả định đơn hàng có thể được User nhập thẳng vào Notion 
    hoặc dùng Make/Zapier đổ về Notion. 
    Script này chỉ dựng form khung (skeleton) cho tương lai.
    """
    logger.info("--- Starting Sync Orders ---")
    
    # Ở phiên bản chạy thực tế, sẽ gọi WooCommerce Rest API 
    # Hoặc Tiktok Shop API để fetch orders từ 'last_sync_time'.
    
    # ... code fetch API ...
    
    # Ghi nhận log
    logger.info("Sync Orders skeleton executed. In MVP, data flows straight to Notion or via this worker if attached to external API.")
    
if __name__ == "__main__":
    sync_orders()
