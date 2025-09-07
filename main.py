#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot - Asosiy fayl (aiogram 3.8)
Bot ishga tushirish uchun ishlatiladi
"""

import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_ID
from handlers import router
from database import db


# Logging sozlamalari
def setup_logging():
    """Logging sistemasini sozlash"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/bot.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    # aiogram loglarini cheklash
    logging.getLogger('aiogram').setLevel(logging.WARNING)
    return logging.getLogger(__name__)


async def main():
    """Botni ishga tushirish"""
    logger = setup_logging()

    # Bot tokenini tekshirish
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ Bot tokenini config.py faylida o'rnating!")
        sys.exit(1)

    if not ADMIN_ID or ADMIN_ID == 123456789:
        logger.error("❌ Admin ID'ni config.py faylida o'rnating!")
        sys.exit(1)

    logger.info("🤖 Bot ishga tushmoqda...")

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=MemoryStorage())

    # Routerni qo'shish
    dp.include_router(router)

    # Bot ma'lumotlarini olish
    try:
        bot_info = await bot.get_me()
        logger.info(f"✅ Bot ishga tushdi: @{bot_info.username}")
        logger.info(f"👤 Admin ID: {ADMIN_ID}")

        # Adminni xabardor qilish
        await bot.send_message(
            ADMIN_ID,
            f"✅ Bot ishga tushdi!\n\n🤖 @{bot_info.username}\n🖥️ ID: <code>{bot_info.id}</code>"
        )

        # Database ma'lumotlari
        all_users = await db.get_all_users()
        logger.info(f"📊 Bazada {len(all_users)} foydalanuvchi")

    except Exception as e:
        logger.error(f"❌ Bot ma'lumotlarini olishda xatolik: {e}")
        sys.exit(1)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=['message', 'callback_query'])

    except KeyboardInterrupt:
        logger.info("🛑 Bot to'xtatildi (Ctrl+C)")
        # Adminni xabardor qilish
        await bot.send_message(ADMIN_ID, "🛑 Bot to'xtatildi (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Bot ishida xatolik: {e}")
        await bot.send_message(ADMIN_ID, f"❌ Botda xatolik: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    # Windows uchun event loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())