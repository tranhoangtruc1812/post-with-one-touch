import os
import asyncio
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes
from app.utils import logger
from scripts.check_reviews import get_posts_ready_for_review, update_post_status, get_post_content_from_blocks

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Giữ track các post đã gửi chờ duyệt để tránh gửi lặp lại
pending_reviews = set()

async def send_post_for_review(context: ContextTypes.DEFAULT_TYPE, post_id: str, topic: str, content: str, image_url: str, scheduled_date: str = "Chưa hẹn giờ"):
    """
    Gửi tin nhắn chứa nội dung bài đăng tới User qua Telegram, kèm nút Approve / Reject
    """
    if post_id in pending_reviews:
        return
        
    chat_id = TELEGRAM_CHAT_ID
    if not chat_id:
        logger.error("TELEGRAM_CHAT_ID is missing")
        return

    message_text = f"📝 *BÀI ĐĂNG CẦN PHÊ DUYỆT*\n\n"
    message_text += f"📌 *Chủ đề:* {topic}\n"
    message_text += f"⏰ *Lịch đăng:* {scheduled_date}\n\n"
    message_text += f"{content[:800]}" # Giới hạn độ dài để đọc dễ
    if len(content) > 800:
        message_text += "...\n*(Nội dung đã được cắt bớt)*"

    keyboard = [
         [
             InlineKeyboardButton("✅ Phê duyệt (Đăng)", callback_data=f"approve_{post_id}"),
             InlineKeyboardButton("❌ Từ chối (Về Draft)", callback_data=f"reject_{post_id}")
         ]
     ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if image_url:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=image_url,
                caption=message_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await context.bot.send_message(
                 chat_id=chat_id,
                 text=message_text,
                 parse_mode='Markdown',
                 reply_markup=reply_markup
            )
        pending_reviews.add(post_id)
        logger.info(f"Đã gửi bài {post_id} qua Telegram để chờ duyệt")
        
        # Cập nhật trạng thái Notion -> Ready for Review
        update_post_status(post_id, "Ready for Review")
        logger.info(f"Đã cập nhật Notion post {post_id} thành 'Ready for Review'.")
    except Exception as e:
        logger.error(f"Lỗi khi gửi tin báo Telegram cho post {post_id}: {e}")

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
     """Lắng nghe sự kiện click button Approve / Reject"""
     query = update.callback_query
     await query.answer()

     data = query.data
     action, post_id = data.split("_", 1)

     if action == "approve":
         success = update_post_status(post_id, "Approved")
         if success:
              await query.edit_message_caption(
                  caption=query.message.caption + "\n\n✅ *Đã phê duyệt! Bài viết sẽ tự động đăng theo lịch.*",
                  parse_mode="Markdown",
                  reply_markup=None # clear buttons
              ) if query.message.photo else await query.edit_message_text(
                  text=query.message.text + "\n\n✅ *Đã phê duyệt! Bài viết sẽ tự động đăng theo lịch.*",
                  parse_mode="Markdown",
                  reply_markup=None
              )
              if post_id in pending_reviews:
                  pending_reviews.remove(post_id)
         else:
              await context.bot.send_message(chat_id=query.message.chat_id, text="⚠️ Lỗi khi cập nhật Notion. Vui lòng check log.")

     elif action == "reject":
         success = update_post_status(post_id, "Draft")
         if success:
              await query.edit_message_caption(
                  caption=query.message.caption + "\n\n❌ *Đã từ chối. Bài viết đã được chuyển về trạng thái Draft.*",
                  parse_mode="Markdown",
                  reply_markup=None
              ) if query.message.photo else await query.edit_message_text(
                  text=query.message.text + "\n\n❌ *Đã từ chối. Bài viết đã được chuyển về trạng thái Draft.*",
                  parse_mode="Markdown",
                  reply_markup=None
              )
              if post_id in pending_reviews:
                  pending_reviews.remove(post_id)
         else:
              await context.bot.send_message(chat_id=query.message.chat_id, text="⚠️ Lỗi khi cập nhật Notion. Vui lòng check log.")

async def check_reviews_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Job chạy định kỳ để fetch Notion check 'Ready for Review' posts
    """
    posts = get_posts_ready_for_review()
    logger.info(f"posts: {posts}")
    if not posts:
        return
        
    for post in posts:
        post_id = post["id"]
        props = post["properties"]
        
        if post_id in pending_reviews:
            continue
            
        content = get_post_content_from_blocks(post_id)
        if not content.strip():
            content = "No content"
        
        topic_chunks = props.get("Topic", {}).get("rich_text", [])
        topic = "".join([c["plain_text"] for c in topic_chunks]) if topic_chunks else "No Topic"
        
        image_url = props.get("Image_URL", {}).get("url", "")
        
        scheduled_date_str = "Chưa hẹn giờ"
        if "Scheduled Date" in props and props["Scheduled Date"]["type"] == "date" and props["Scheduled Date"]["date"]:
            raw_date = props["Scheduled Date"]["date"]["start"]
            try:
                import datetime
                dt = datetime.datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
                # Hiển thị lại với format ngày giờ cho thân thiện, ví dụ: 2026-04-19 10:00
                scheduled_date_str = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                scheduled_date_str = raw_date
        
        await send_post_for_review(context, post_id, topic, content, image_url, scheduled_date_str)
