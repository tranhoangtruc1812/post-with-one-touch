import os
import asyncio
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CallbackQueryHandler
from app.utils import logger
from scripts.telegram_bot import button_callback_handler, check_reviews_job

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def run_bot():
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_bot_token":
        logger.error("Missing TELEGRAM_BOT_TOKEN. Please set it in .env")
        return

    logger.info("Khởi động Telegram Bot...")
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Thêm handler xử lý event khi user bấm nút
    application.add_handler(CallbackQueryHandler(button_callback_handler))

    # Thêm job (chạy qua JobQueue của python-telegram-bot) để quét Notion mỗi 5 phút
    job_queue = application.job_queue
    job_queue.run_repeating(check_reviews_job, interval=30, first=10) # 300s = 5 phút

    logger.info("Bot đang chờ tín hiệu... Bấm Ctrl+C để dừng.")
    application.run_polling()

if __name__ == '__main__':
    run_bot()
