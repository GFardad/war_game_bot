"""
ربات جنگ جهانی - فایل اصلی
برای اجرا: python main.py
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

import config
from database import init_database
from handlers import register_handlers
from scheduler import start_schedulers

# تنظیم لاگ
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """اجرا هنگام شروع ربات"""
    logger.info("🤖 ربات شروع به کار کرد...")
    
    # اطلاع‌رسانی به ادمین‌ها
    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                "✅ ربات جنگ جهانی فعال شد!\n\n"
                "⚙️ برای مدیریت، از منوی اصلی گزینه '📢 پیام مدیریت' را بزنید."
            )
        except Exception as e:
            logger.error(f"خطا در ارسال پیام به ادمین {admin_id}: {e}")


async def on_shutdown(bot: Bot):
    """اجرا هنگام خاموش شدن ربات"""
    logger.info("🛑 ربات خاموش شد...")


async def main():
    """تابع اصلی"""
    
    # بررسی توکن
    if config.BALEBOT_TOKEN == "YOUR_BALEBOT_TOKEN_HERE":
        logger.error("❌ لطفاً توکن ربات را در config.py وارد کنید!")
        return
    
    # ایجاد دیتابیس
    logger.info("📦 ایجاد دیتابیس...")
    await init_database()
    
    # ایجاد ربات
    bot = Bot(token=config.BALEBOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # ثبت هندلرها
    register_handlers(dp)
    
    # شروع زمان‌بندها
    asyncio.create_task(start_schedulers(bot))
    
    # اجرای ربات
    logger.info("🚀 ربات در حال اجرا است...")
    
    try:
        await dp.start_polling(
            bot,
            on_startup=on_startup,
            on_shutdown=on_shutdown
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⛔ ربات توسط کاربر متوقف شد.")