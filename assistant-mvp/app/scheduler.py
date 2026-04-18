from apscheduler.schedulers.blocking import BlockingScheduler
from app.utils import logger

# Import worker scripts
from scripts.generate_posts import run_content_agent
from scripts.publish_posts import run_publish_agent
from scripts.sync_orders import sync_orders
from scripts.reply_suggestions import run_order_agent
from scripts.daily_report import run_report_agent
from run_bot import run_bot

def start_scheduler():
    logger.info("Khởi tạo APScheduler...")
    scheduler = BlockingScheduler()
    
    # Lịch đã ấn định theo spec
    # 08:00: generate_posts
    scheduler.add_job(run_content_agent, 'cron', hour=8, minute=0, id='gen_posts')
    
    # 11:30 and 15:00: check approved posts
    scheduler.add_job(run_publish_agent, 'cron', hour=11, minute=30, id='pub_posts_1')
    scheduler.add_job(run_publish_agent, 'cron', hour=15, minute=0, id='pub_posts_2')
    
    # Mỗi 10 phút: sync_orders và xử lý
    scheduler.add_job(sync_orders, 'interval', minutes=10, id='sync_ord')
    scheduler.add_job(run_order_agent, 'interval', minutes=10, id='reply_sugg')
    
    # 20:30: daily_report
    scheduler.add_job(run_report_agent, 'cron', hour=20, minute=30, id='daily_rep')
    
    run_bot()
    logger.info("Hệ thống Scheduler đã kích hoạt! Bấm Ctrl+C để thoát.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Hệ thống đã dừng lại.")
