from apscheduler.schedulers.blocking import BlockingScheduler
from app.utils import logger

from datetime import datetime
import threading

# Import worker scripts
from scripts.generate_posts import run_content_agent
from scripts.generate_image import run_image_agent
from scripts.publish_posts import run_publish_agent
# from scripts.sync_orders import sync_orders
# from scripts.reply_suggestions import run_order_agent
from scripts.daily_report import run_report_agent
from run_bot import run_bot

def start_scheduler():
    logger.info("Khởi tạo APScheduler...")
    scheduler = BlockingScheduler()
    logger.info(f"Current time: {datetime.now()}")

    # Lịch đã ấn định theo spec
    scheduler.add_job(run_content_agent, 'cron', hour=14, minute=0, id='gen_posts')
    scheduler.add_job(run_image_agent, 'cron', hour=15, minute=0, id='gen_image')
    # check approved posts mỗi 4 phút
    scheduler.add_job(run_publish_agent, 'interval', minutes=60*2, id='pub_posts_1')

    # Mỗi 10 phút: sync_orders và xử lý
    # scheduler.add_job(sync_orders, 'interval', minutes=10, id='sync_ord')
    # scheduler.add_job(run_order_agent, 'interval', minutes=10, id='reply_sugg')

    # 20:30: daily_report
    scheduler.add_job(run_report_agent, 'cron', hour=18, minute=30, id='daily_rep')

    # Chạy scheduler trên background thread để không block Telegram bot
    def run_scheduler():
        logger.info("Hệ thống Scheduler đã kích hoạt!")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler đã dừng lại.")

    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True, name="scheduler")
    scheduler_thread.start()

    # run_bot() dùng run_polling() nên phải chạy trên main thread
    run_bot()
