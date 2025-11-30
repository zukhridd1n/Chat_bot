#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram bot handlerlari (aiogram 3.8)
Barcha komandalar va xabar handlerlarini o'z ichiga oladi
"""

import logging
from datetime import datetime
from typing import Dict

from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ADMIN_ID, Messages, Errors, Settings, Formats, CallbackData
from database import db
from utils import is_admin, split_long_message, escape_html, format_file_size, extract_user_id_from_message

logger = logging.getLogger(__name__)
router = Router()

# Admin reply rejimi - user_id saqlab qolish uchun
admin_reply_mode: Dict[int, int] = {}


# =============================================================================
# YORDAMCHI FUNKSIYALAR
# =============================================================================

async def get_media_info(message: Message) -> str:
    """Media haqida ma'lumot olish"""
    info = ""

    if message.photo:
        photo = message.photo[-1]
        size = format_file_size(photo.file_size or 0)
        info = f"📷 Rasm yuborildi\n• Hajmi: {size}"

    elif message.video:
        video = message.video
        size = format_file_size(video.file_size or 0)
        duration = f"{video.duration // 60}:{video.duration % 60:02d}" if video.duration else "Noma'lum"
        resolution = f"{video.width}x{video.height}" if video.width and video.height else "Noma'lum"
        info = f"🎥 Video yuborildi\n• Hajmi: {size}\n• Davomiyligi: {duration}\n• O'lchami: {resolution}"

    elif message.audio:
        audio = message.audio
        size = format_file_size(audio.file_size or 0)
        duration = f"{audio.duration // 60}:{audio.duration % 60:02d}" if audio.duration else "Noma'lum"
        performer = audio.performer or "Noma'lum"
        title = audio.title or "Noma'lum"
        info = f"🎵 Audio yuborildi\n• Ijrochi: {performer}\n• Sarlavha: {title}\n• Davomiyligi: {duration}\n• Hajmi: {size}"

    elif message.voice:
        voice = message.voice
        size = format_file_size(voice.file_size or 0)
        duration = f"{voice.duration // 60}:{voice.duration % 60:02d}" if voice.duration else "Noma'lum"
        info = f"🎤 Ovozli xabar yuborildi\n• Davomiyligi: {duration}\n• Hajmi: {size}"

    elif message.video_note:
        video_note = message.video_note
        size = format_file_size(video_note.file_size or 0)
        duration = f"{video_note.duration // 60}:{video_note.duration % 60:02d}" if video_note.duration else "Noma'lum"
        info = f"🎬 Video xabar yuborildi\n• Davomiyligi: {duration}\n• Hajmi: {size}"

    elif message.document:
        document = message.document
        size = format_file_size(document.file_size or 0)
        file_name = document.file_name or "Noma'lum fayl"
        mime_type = document.mime_type or "Noma'lum"

        # APK fayllarini bloklash
        if file_name.lower().endswith('.apk') or mime_type == 'application/vnd.android.package-archive':
            raise ValueError("APK fayllari ruxsat etilmagan!")

        info = f"📄 Hujjat yuborildi\n• Nomi: {file_name}\n• Hajmi: {size}\n• Turi: {mime_type}"

    elif message.sticker:
        sticker = message.sticker
        size = format_file_size(sticker.file_size or 0)
        emoji = sticker.emoji or "🙂"
        set_name = sticker.set_name or "Noma'lum"
        info = f"😄 Stiker yuborildi\n• Emoji: {emoji}\n• To'plam: {set_name}\n• Hajmi: {size}"

    elif message.animation:
        animation = message.animation
        size = format_file_size(animation.file_size or 0)
        duration = f"{animation.duration // 60}:{animation.duration % 60:02d}" if animation.duration else "Noma'lum"
        info = f"🎭 GIF yuborildi\n• Davomiyligi: {duration}\n• Hajmi: {size}"

    elif message.location:
        location = message.location
        info = f"📍 Joylashuv yuborildi\n• Kenglik: {location.latitude}\n• Uzunlik: {location.longitude}"

    elif message.venue:
        venue = message.venue
        info = f"🏢 Joy yuborildi\n• Nomi: {venue.title}\n• Manzil: {venue.address}"

    elif message.contact:
        contact = message.contact
        phone = contact.phone_number or "Noma'lum"
        first_name = contact.first_name or "Noma'lum"
        last_name = contact.last_name or ""
        info = f"📞 Kontakt yuborildi\n• Ism: {first_name} {last_name}\n• Telefon: {phone}"

    elif message.poll:
        poll = message.poll
        options = "\n".join([f"• {opt.text}" for opt in poll.options])
        info = f"📊 So'rovnoma yuborildi\n• Savol: {poll.question}\n• Variantlar:\n{options}"

    elif message.dice:
        dice = message.dice
        emoji_names = {
            "🎲": "Zar",
            "🎯": "Nishon",
            "🎰": "Slotlar",
            "⚽": "Futbol",
            "🏀": "Basketbol",
            "🎳": "Bouling"
        }
        emoji_name = emoji_names.get(dice.emoji, "O'yin")
        info = f"🎮 {emoji_name} yuborildi\n• Natija: {dice.value}\n• Emoji: {dice.emoji}"

    if message.caption:
        info += f"\n\n📝 Izoh: {message.caption}"

    return info


async def forward_media_to_admin(message: Message, user, media_info: str):
    """Media ni adminga forward qilish"""
    try:
        # Media ni forward qilish
        await message.forward(ADMIN_ID)

        # Ma'lumot xabarini yuborish
        timestamp = datetime.now().strftime(Formats.DATETIME_FORMAT)
        admin_notification = f"""
🔔 <b>Yangi media xabar keldi!</b>

👤 <b>Foydalanuvchi:</b>
• Ism: {user.first_name} {user.last_name or ''}
• Username: @{user.username or 'Mavjud emas'}
• ID: <code>{user.id}</code>
• Vaqt: {timestamp}

📎 <b>Media ma'lumotlari:</b>
{media_info}

📤 <b>Javob berish:</b>
<code>/reply {user.id}</code>
"""

        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="💬 Javob berish", callback_data=f"reply_{user.id}")
        keyboard.button(text="👤 Foydalanuvchi", callback_data=f"user_{user.id}")
        keyboard.adjust(2)

        await message.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_notification,
            reply_markup=keyboard.as_markup()
        )

        return True
    except Exception as e:
        logger.error(f"Adminga forward qilishda xatolik: {e}")
        return False


async def send_admin_media_to_user(message: Message, user_id: int):
    """Admin media ni foydalanuvchiga yuborish"""
    try:
        bot = message.bot
        caption_text = f"💬 <b>Xodimundan javob:</b>"

        if message.caption:
            caption_text += f"\n\n{message.caption}"

        if message.photo:
            await bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=caption_text)
        elif message.video:
            await bot.send_video(chat_id=user_id, video=message.video.file_id, caption=caption_text)
        elif message.audio:
            await bot.send_audio(chat_id=user_id, audio=message.audio.file_id, caption=caption_text)
        elif message.voice:
            await bot.send_voice(chat_id=user_id, voice=message.voice.file_id)
            await bot.send_message(chat_id=user_id, text=caption_text)
        elif message.video_note:
            await bot.send_video_note(chat_id=user_id, video_note=message.video_note.file_id)
            await bot.send_message(chat_id=user_id, text=caption_text)
        elif message.document:
            await bot.send_document(chat_id=user_id, document=message.document.file_id, caption=caption_text)
        elif message.sticker:
            await bot.send_sticker(chat_id=user_id, sticker=message.sticker.file_id)
            await bot.send_message(chat_id=user_id, text=caption_text)
        elif message.animation:
            await bot.send_animation(chat_id=user_id, animation=message.animation.file_id, caption=caption_text)
        elif message.location:
            await bot.send_location(chat_id=user_id, latitude=message.location.latitude,
                                    longitude=message.location.longitude)
            await bot.send_message(chat_id=user_id, text=caption_text)
        elif message.venue:
            await bot.send_venue(
                chat_id=user_id,
                latitude=message.venue.location.latitude,
                longitude=message.venue.location.longitude,
                title=message.venue.title,
                address=message.venue.address
            )
            await bot.send_message(chat_id=user_id, text=caption_text)
        elif message.contact:
            await bot.send_contact(
                chat_id=user_id,
                phone_number=message.contact.phone_number,
                first_name=message.contact.first_name,
                last_name=message.contact.last_name or ""
            )
            await bot.send_message(chat_id=user_id, text=caption_text)

        return True
    except Exception as e:
        logger.error(f"Admin media yuborishda xatolik: {e}")
        return False


# =============================================================================
# KOMANDA HANDLERLARI
# =============================================================================

@router.message(CommandStart())
async def start_handler(message: Message):
    """Start komandasi handleri"""
    try:
        user = message.from_user
        logger.info(f"👤 /start - {user.first_name} ({user.id})")

        if is_admin(user.id):
            await message.answer(Messages.START_ADMIN)
            logger.info(f"🔧 Admin start: {user.first_name} ({user.id})")
        else:
            await message.answer(Messages.START)

    except Exception as e:
        logger.error(f"Start handler xatoligi: {e}")
        await message.answer(Errors.GENERAL_ERROR)


@router.message(Command("help"))
async def help_handler(message: Message):
    """Help komandasi handleri"""
    try:
        user = message.from_user
        logger.info(f"❓ /help - {user.first_name} ({user.id})")

        if is_admin(user.id):
            await message.answer(Messages.HELP_ADMIN)
        else:
            await message.answer(Messages.HELP_USER)

    except Exception as e:
        logger.error(f"Help handler xatoligi: {e}")
        await message.answer(Errors.GENERAL_ERROR)


@router.message(Command("messages"))
async def messages_handler(message: Message):
    """Barcha xabarlarni ko'rish (faqat admin)"""
    try:
        user = message.from_user

        if not is_admin(user.id):
            await message.answer(Errors.ADMIN_ONLY)
            return

        logger.info(f"📋 /messages - {user.first_name} ({user.id})")

        stats = await db.get_stats()
        all_users = await db.get_all_users()

        if not all_users:
            await message.answer(Errors.NO_MESSAGES)
            return

        stats_text = f"""
📊 <b>Bot Statistikasi</b>

👥 Jami foydalanuvchilar: {stats['total_users']}
💬 Jami xabarlar: {stats['total_messages']}
🔔 Javob kutayotgan: {stats['unread_messages']}
🟢 Faol (24h): {stats['active_users_24h']}

📋 <b>Foydalanuvchilar:</b>
"""

        await message.answer(stats_text)

        users_list = list(all_users.items())
        page_size = 5

        for i in range(0, len(users_list), page_size):
            page_users = users_list[i:i + page_size]
            response_parts = []

            for user_id, user_data in page_users:
                user_info = user_data.user_info
                messages = user_data.messages
                user_messages = [m for m in messages if m.type == "user"]
                admin_replies = [m for m in messages if m.type == "admin"]

                status_emoji = ""
                last_message = ""
                if messages:
                    last_msg = messages[-1]
                    last_message = escape_html(last_msg.text[:50])
                    if len(last_msg.text) > 50:
                        last_message += "..."

                    if last_msg.type == 'user':
                        status_emoji = "❗️"

                user_block = f"""
👤 <b>{escape_html(user_info.first_name)} {escape_html(user_info.last_name or '')}</b>
🆔 ID: <code>{user_id}</code>
📱 @{user_info.username or 'Mavjud emas'}
💬 Xabarlar: {len(user_messages)} | Javoblar: {len(admin_replies)}
📝 So'nggi: {last_message} {status_emoji}

➡️ <code>/reply {user_id}</code>

{'=' * 30}
"""
                response_parts.append(user_block)

            page_text = "\n".join(response_parts)
            if len(page_text) > Settings.MAX_MESSAGE_LENGTH:
                for part in split_long_message(page_text):
                    await message.answer(part)
            else:
                await message.answer(page_text)

    except Exception as e:
        logger.error(f"Messages handler xatoligi: {e}")
        await message.answer(Errors.GENERAL_ERROR)


@router.message(Command("stats"))
async def stats_handler(message: Message):
    """Bot statistikasi (faqat admin)"""
    try:
        user = message.from_user

        if not is_admin(user.id):
            await message.answer(Errors.ADMIN_ONLY)
            return

        logger.info(f"📊 /stats - {user.first_name} ({user.id})")

        stats = await db.get_stats()

        top_users_text = ""
        for i, top_user in enumerate(stats['top_users'], 1):
            top_users_text += f"{i}. {escape_html(top_user['name'])} - {top_user['messages_count']} xabar\n"

        stats_message = f"""
📊 <b>To'liq Bot Statistikasi</b>

👥 <b>Foydalanuvchilar:</b>
• Jami: {stats['total_users']}
• Faol (24h): {stats['active_users_24h']}

💬 <b>Xabarlar:</b>
• Jami: {stats['total_messages']}
• Javob kutayotgan: {stats['unread_messages']}

🏆 <b>Eng faol foydalanuvchilar:</b>
{top_users_text or "Ma'lumot yo'q"}

📅 <b>Vaqt:</b> {datetime.now().strftime(Formats.DATETIME_FORMAT)}
"""

        await message.answer(stats_message)

    except Exception as e:
        logger.error(f"Stats handler xatoligi: {e}")
        await message.answer(Errors.GENERAL_ERROR)


@router.message(Command("reply"))
async def reply_handler(message: Message):
    """Foydalanuvchiga javob berish (faqat admin)"""
    try:
        user = message.from_user

        if not is_admin(user.id):
            await message.answer(Errors.ADMIN_ONLY)
            return

        logger.info(f"💬 /reply - {user.first_name} ({user.id})")

        command_parts = message.text.split(' ', 2)

        # Faqat user_id berilgan bo'lsa - reply rejimi yoqish
        if len(command_parts) == 2:
            try:
                target_user_id = int(command_parts[1])
            except ValueError:
                await message.answer(Errors.INVALID_USER_ID)
                return

            # Foydalanuvchini tekshirish
            user_data = await db.get_user_data(target_user_id)
            if not user_data:
                await message.answer(Errors.USER_NOT_FOUND)
                return

            if await db.is_user_blocked(target_user_id):
                await message.answer("⚠️ Bu foydalanuvchi bloklangan!")
                return

            # Reply rejimini yoqish
            admin_reply_mode[user.id] = target_user_id

            await message.answer(f"""
✅ <b>Javob rejimi yoqildi!</b>

👤 <b>Foydalanuvchi:</b> {escape_html(user_data.user_info.first_name)} {escape_html(user_data.user_info.last_name or '')}
🆔 <b>ID:</b> <code>{target_user_id}</code>

📝 <b>Endi quyidagilarni yuborishingiz mumkin:</b>
• Matn xabar
• Rasm, video, audio
• Hujjat, stiker, GIF
• Joylashuv, kontakt

💡 Keyingi xabaringiz avtomatik foydalanuvchiga yuboriladi!
""")
            return

        # To'liq komanda - tezkor matn javob
        if len(command_parts) >= 3:
            try:
                target_user_id = int(command_parts[1])
                reply_text = command_parts[2]
            except ValueError:
                await message.answer(Errors.INVALID_USER_ID)
                return

            user_data = await db.get_user_data(target_user_id)
            if not user_data:
                await message.answer(Errors.USER_NOT_FOUND)
                return

            if await db.is_user_blocked(target_user_id):
                await message.answer("⚠️ Bu foydalanuvchi bloklangan!")
                return

            try:
                bot = message.bot
                await bot.send_message(
                    chat_id=target_user_id,
                    text=f"💬 <b>Xodimundan xabar:</b>\n\n{escape_html(reply_text)}"
                )

                if await db.add_admin_reply(target_user_id, reply_text):
                    await message.answer(Errors.REPLY_SUCCESS)
                    logger.info(f"✅ Tezkor javob yuborildi: {target_user_id}")
                else:
                    await message.answer("⚠️ Javob yuborildi, lekin saqlashda muammo!")

            except Exception as e:
                logger.error(f"Javob yuborishda xatolik: {e}")
                await message.answer(f"{Errors.REPLY_ERROR}\n\nXatolik: {str(e)}")
            return

        # Noto'g'ri format
        await message.answer(Errors.INVALID_REPLY_FORMAT)

    except Exception as e:
        logger.error(f"Reply handler xatoligi: {e}")
        await message.answer(Errors.GENERAL_ERROR)


@router.message(Command("search"))
async def search_handler(message: Message):
    """Xabarlarda qidirish (faqat admin)"""
    try:
        user = message.from_user

        if not is_admin(user.id):
            await message.answer(Errors.ADMIN_ONLY)
            return

        command_parts = message.text.split(' ', 1)
        if len(command_parts) < 2:
            await message.answer("❌ Qidiruv so'zini kiriting!\n\nMisol: <code>/search salom</code>")
            return

        query = command_parts[1]
        logger.info(f"🔍 /search '{query}' - {user.first_name} ({user.id})")

        results = await db.search_messages(query, limit=20)

        if not results:
            await message.answer(Errors.NO_SEARCH_RESULTS)
            return

        search_results = f"🔍 <b>Qidiruv natijalari: '{escape_html(query)}'</b>\n\n"

        for i, result in enumerate(results[:10], 1):
            user_name = escape_html(result['user_name'])
            username = result['username'] or 'Mavjud emas'
            match_text = escape_html(result['match_text'][:100])
            if len(result['match_text']) > 100:
                match_text += "..."

            search_results += f"""
{i}. 👤 <b>{user_name}</b> (@{username})
📝 {match_text}
⏰ {result['message'].timestamp}
🆔 <code>/reply {result['user_id']}</code>

"""

        if len(results) > 10:
            search_results += f"\n... va yana {len(results) - 10} natija"

        for part in split_long_message(search_results):
            await message.answer(part)

    except Exception as e:
        logger.error(f"Search handler xatoligi: {e}")
        await message.answer(Errors.GENERAL_ERROR)


@router.message(Command("backup"))
async def backup_handler(message: Message):
    """Ma'lumotlar zaxirasi (faqat admin)"""
    try:
        user = message.from_user

        if not is_admin(user.id):
            await message.answer(Errors.ADMIN_ONLY)
            return

        logger.info(f"💾 /backup - {user.first_name} ({user.id})")

        if await db.backup_data():
            stats = await db.get_stats()
            backup_info = f"""
💾 <b>Zaxira muvaffaqiyatli yaratildi!</b>

📊 <b>Zaxiralangan ma'lumotlar:</b>
• Foydalanuvchilar: {stats['total_users']}
• Xabarlar: {stats['total_messages']}
• Vaqt: {datetime.now().strftime(Formats.DATETIME_FORMAT)}
"""
            await message.answer(backup_info)
        else:
            await message.answer(Errors.BACKUP_ERROR)

    except Exception as e:
        logger.error(f"Backup handler xatoligi: {e}")
        await message.answer(Errors.GENERAL_ERROR)


# =============================================================================
# USER MEDIA HANDLERLARI
# =============================================================================

@router.message(F.photo & F.from_user.func(lambda user: not is_admin(user.id)))
async def user_photo_handler(message: Message):
    """User rasm handleri"""
    await user_media_handler(message, "photo")


@router.message(F.video & F.from_user.func(lambda user: not is_admin(user.id)))
async def user_video_handler(message: Message):
    """User video handleri"""
    await user_media_handler(message, "video")


@router.message(F.audio & F.from_user.func(lambda user: not is_admin(user.id)))
async def user_audio_handler(message: Message):
    """User audio handleri"""
    await user_media_handler(message, "audio")


@router.message(F.voice & F.from_user.func(lambda user: not is_admin(user.id)))
async def user_voice_handler(message: Message):
    """User ovozli xabar handleri"""
    await user_media_handler(message, "voice")


@router.message(F.video_note & F.from_user.func(lambda user: not is_admin(user.id)))
async def user_video_note_handler(message: Message):
    """User video xabar handleri"""
    await user_media_handler(message, "video_note")


@router.message(F.document & F.from_user.func(lambda user: not is_admin(user.id)))
async def user_document_handler(message: Message):
    """User hujjat handleri"""
    try:
        # APK fayllarini tekshirish
        document = message.document
        if document:
            file_name = document.file_name or ""
            mime_type = document.mime_type or ""

            if (file_name.lower().endswith('.apk') or
                    mime_type == 'application/vnd.android.package-archive'):
                await message.answer("❌ APK fayllari yuborish taqiqlangan!")
                logger.warning(f"🚫 APK fayl rad etildi: {message.from_user.id}")
                return

        await user_media_handler(message, "document")

    except Exception as e:
        logger.error(f"User document handler xatoligi: {e}")
        await message.answer(Errors.GENERAL_ERROR)


@router.message(F.sticker & F.from_user.func(lambda user: not is_admin(user.id)))
async def user_sticker_handler(message: Message):
    """User stiker handleri"""
    await user_media_handler(message, "sticker")


@router.message(F.animation & F.from_user.func(lambda user: not is_admin(user.id)))
async def user_animation_handler(message: Message):
    """User GIF handleri"""
    await user_media_handler(message, "animation")


@router.message(F.location & F.from_user.func(lambda user: not is_admin(user.id)))
async def user_location_handler(message: Message):
    """User joylashuv handleri"""
    await user_media_handler(message, "location")


@router.message(F.venue & F.from_user.func(lambda user: not is_admin(user.id)))
async def user_venue_handler(message: Message):
    """User joy handleri"""
    await user_media_handler(message, "venue")


@router.message(F.contact & F.from_user.func(lambda user: not is_admin(user.id)))
async def user_contact_handler(message: Message):
    """User kontakt handleri"""
    await user_media_handler(message, "contact")


@router.message(F.poll & F.from_user.func(lambda user: not is_admin(user.id)))
async def user_poll_handler(message: Message):
    """User so'rovnoma handleri"""
    await user_media_handler(message, "poll")


@router.message(F.dice & F.from_user.func(lambda user: not is_admin(user.id)))
async def user_dice_handler(message: Message):
    """User zar/o'yin handleri"""
    await user_media_handler(message, "dice")


async def user_media_handler(message: Message, media_type: str):
    """User media handleri"""
    try:
        user = message.from_user

        # Bloklangan foydalanuvchilarni tekshirish
        if await db.is_user_blocked(user.id):
            logger.info(f"🚫 Bloklangan foydalanuvchi: {user.first_name} ({user.id})")
            return

        logger.info(f"🎭 {media_type.upper()} - {user.first_name} ({user.id})")

        # Media ma'lumotlarini olish
        try:
            media_info = await get_media_info(message)
        except ValueError as ve:
            await message.answer(f"❌ {str(ve)}")
            return

        # Foydalanuvchi ma'lumotlarini tayyorlash
        user_dict = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username
        }

        # Xabarni saqlash
        if await db.add_user_message(user.id, user_dict, media_info, message.message_id):
            # Foydalanuvchiga tasdiq xabari
            await message.answer(Messages.MESSAGE_RECEIVED)

            # Adminga forward qilish
            await forward_media_to_admin(message, user, media_info)
        else:
            await message.answer("❌ Xatolik yuz berdi, qaytadan urinib ko'ring!")

    except Exception as e:
        logger.error(f"{media_type} handler xatoligi: {e}")
        await message.answer(Errors.GENERAL_ERROR)


# =============================================================================
# ADMIN MEDIA HANDLERLARI (Reply rejimida)
# =============================================================================

@router.message(F.photo & F.from_user.func(lambda user: is_admin(user.id)))
async def admin_photo_handler(message: Message):
    """Admin rasm handleri"""
    await admin_media_handler(message)


@router.message(F.video & F.from_user.func(lambda user: is_admin(user.id)))
async def admin_video_handler(message: Message):
    """Admin video handleri"""
    await admin_media_handler(message)


@router.message(F.audio & F.from_user.func(lambda user: is_admin(user.id)))
async def admin_audio_handler(message: Message):
    """Admin audio handleri"""
    await admin_media_handler(message)


@router.message(F.voice & F.from_user.func(lambda user: is_admin(user.id)))
async def admin_ovozli_handler(message: Message):
    """Admin ovozli xabar handleri"""
    await admin_media_handler(message)


@router.message(F.video_note & F.from_user.func(lambda user: is_admin(user.id)))
async def admin_video_note_handler(message: Message):
    """Admin video xabar handleri"""
    await admin_media_handler(message)


@router.message(F.document & F.from_user.func(lambda user: is_admin(user.id)))
async def admin_document_handler(message: Message):
    """Admin hujjat handleri"""
    await admin_media_handler(message)


@router.message(F.sticker & F.from_user.func(lambda user: is_admin(user.id)))
async def admin_sticker_handler(message: Message):
    """Admin stiker handleri"""
    await admin_media_handler(message)


@router.message(F.animation & F.from_user.func(lambda user: is_admin(user.id)))
async def admin_animation_handler(message: Message):
    """Admin GIF handleri"""
    await admin_media_handler(message)


@router.message(F.location & F.from_user.func(lambda user: is_admin(user.id)))
async def admin_location_handler(message: Message):
    """Admin joylashuv handleri"""
    await admin_media_handler(message)


@router.message(F.venue & F.from_user.func(lambda user: is_admin(user.id)))
async def admin_venue_handler(message: Message):
    """Admin joy handleri"""
    await admin_media_handler(message)


@router.message(F.contact & F.from_user.func(lambda user: is_admin(user.id)))
async def admin_contact_handler(message: Message):
    """Admin kontakt handleri"""
    await admin_media_handler(message)


async def admin_media_handler(message: Message):
    """Admin media handleri"""
    try:
        user = message.from_user

        # Reply rejimini tekshirish
        if user.id not in admin_reply_mode:
            await message.answer("""
❌ <b>Media yuborish uchun:</b>

1️⃣ Avval <code>/reply &lt;user_id&gt;</code> yuboring
2️⃣ Keyin media faylni yuboring

💡 <b>Misol:</b>
<code>/reply 123456789</code>
Keyin rasm/video/audio yuboring
""")
            return

        target_user_id = admin_reply_mode[user.id]

        # Foydalanuvchini tekshirish
        user_data = await db.get_user_data(target_user_id)
        if not user_data:
            admin_reply_mode.pop(user.id, None)
            await message.answer(Errors.USER_NOT_FOUND)
            return

        if await db.is_user_blocked(target_user_id):
            admin_reply_mode.pop(user.id, None)
            await message.answer("⚠️ Bu foydalanuvchi bloklangan!")
            return

        # Media yuborish
        success = await send_admin_media_to_user(message, target_user_id)

        if success:
            # Ma'lumotni bazaga saqlash
            media_info = await get_media_info(message)
            if await db.add_admin_reply(target_user_id, media_info):
                await message.answer("✅ Media javob muvaffaqiyatli yuborildi!")
                logger.info(f"✅ Media javob yuborildi: {target_user_id}")
            else:
                await message.answer("⚠️ Media yuborildi, lekin saqlashda muammo!")

            # Reply rejimini o'chirish
            admin_reply_mode.pop(user.id, None)
        else:
            await message.answer("❌ Media yuborishda xatolik yuz berdi!")

    except Exception as e:
        logger.error(f"Admin media handler xatoligi: {e}")
        await message.answer(Errors.GENERAL_ERROR)


# =============================================================================
# ADMIN MATN HANDLERI
# =============================================================================

@router.message(F.text & F.from_user.func(lambda user: is_admin(user.id)))
async def admin_text_handler(message: Message):
    """Admin matn handleri"""
    try:
        user = message.from_user

        # Komandalarni e'tiborsiz qoldirish
        if message.text.startswith('/'):
            return

        # Reply rejimini tekshirish
        if user.id not in admin_reply_mode:
            help_text = """
🔧 <b>Siz adminsiz!</b>

📝 <b>Matn javob berish:</b>
<code>/reply &lt;user_id&gt; &lt;xabar&gt;</code>

📎 <b>Media javob berish:</b>
1️⃣ <code>/reply &lt;user_id&gt;</code>
2️⃣ Media faylni yuboring

Barcha komandalar: /help
"""
            await message.answer(help_text)
            return

        target_user_id = admin_reply_mode[user.id]

        # Foydalanuvchini tekshirish
        user_data = await db.get_user_data(target_user_id)
        if not user_data:
            admin_reply_mode.pop(user.id, None)
            await message.answer(Errors.USER_NOT_FOUND)
            return

        if await db.is_user_blocked(target_user_id):
            admin_reply_mode.pop(user.id, None)
            await message.answer("⚠️ Bu foydalanuvchi bloklangan!")
            return

        # Matn javob yuborish
        try:
            bot = message.bot
            await bot.send_message(
                chat_id=target_user_id,
                text=f"💬 <b>Xodimundan xabar:</b>\n\n{escape_html(message.text)}"
            )

            if await db.add_admin_reply(target_user_id, message.text):
                await message.answer("✅ Javob muvaffaqiyatli yuborildi!")
                logger.info(f"✅ Matn javob yuborildi: {target_user_id}")
            else:
                await message.answer("⚠️ Javob yuborildi, lekin saqlashda muammo!")

            # Reply rejimini o'chirish
            admin_reply_mode.pop(user.id, None)

        except Exception as e:
            logger.error(f"Matn javob yuborishda xatolik: {e}")
            await message.answer(f"{Errors.REPLY_ERROR}\n\nXatolik: {str(e)}")

    except Exception as e:
        logger.error(f"Admin text handler xatoligi: {e}")
        await message.answer(Errors.GENERAL_ERROR)


# =============================================================================
# USER MATN HANDLERI
# =============================================================================

@router.message(F.text & F.from_user.func(lambda user: not is_admin(user.id)))
async def user_text_handler(message: Message):
    """User matn xabar handleri"""
    try:
        user = message.from_user
        message_text = message.text

        # Bloklangan foydalanuvchilarni tekshirish
        if await db.is_user_blocked(user.id):
            logger.info(f"🚫 Bloklangan foydalanuvchi: {user.first_name} ({user.id})")
            return

        logger.info(f"💬 Matn xabar - {user.first_name} ({user.id}): {message_text[:50]}...")

        # Foydalanuvchi ma'lumotlarini tayyorlash
        user_dict = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username
        }

        # Xabarni saqlash
        if await db.add_user_message(user.id, user_dict, message_text, message.message_id):
            # Foydalanuvchiga tasdiq
            await message.answer(Messages.MESSAGE_RECEIVED)

            # Adminga bildirishnoma
            try:
                timestamp = datetime.now().strftime(Formats.DATETIME_FORMAT)
                admin_notification = Messages.admin_notification(
                    user, message_text, timestamp, user.id
                )

                # Inline keyboard qo'shish
                keyboard = InlineKeyboardBuilder()
                keyboard.button(
                    text="💬 Javob berish",
                    callback_data=f"reply_{user.id}"
                )
                keyboard.button(
                    text="👤 Foydalanuvchi",
                    callback_data=f"user_{user.id}"
                )
                keyboard.adjust(2)

                bot = message.bot
                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=admin_notification,
                    reply_markup=keyboard.as_markup()
                )

            except Exception as e:
                logger.error(f"Adminga xabar yuborishda xatolik: {e}")
        else:
            await message.answer("❌ Xatolik yuz berdi, qaytadan urinib ko'ring!")

    except Exception as e:
        logger.error(f"User text handler xatoligi: {e}")
        await message.answer(Errors.GENERAL_ERROR)


# =============================================================================
# CALLBACK HANDLERLARI
# =============================================================================

@router.callback_query(F.data.startswith("reply_"))
async def reply_callback_handler(callback: CallbackQuery):
    """Javob berish callback handleri"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return

        user_id = int(callback.data.split("_")[1])

        # Reply rejimini yoqish
        admin_reply_mode[callback.from_user.id] = user_id

        reply_text = f"""
✅ <b>Javob rejimi yoqildi!</b>

👤 <b>Foydalanuvchi ID:</b> <code>{user_id}</code>

📝 <b>Endi yuborishingiz mumkin:</b>
• Matn xabar
• Rasm, video, audio
• Hujjat, stiker, GIF
• Joylashuv, kontakt

💡 Keyingi xabaringiz avtomatik foydalanuvchiga yuboriladi!
"""

        await callback.message.answer(reply_text)
        await callback.answer("Javob rejimi yoqildi!")

    except Exception as e:
        logger.error(f"Reply callback xatoligi: {e}")
        await callback.answer("❌ Xatolik yuz berdi!")


@router.callback_query(F.data.startswith("user_"))
async def user_info_callback_handler(callback: CallbackQuery):
    """Foydalanuvchi ma'lumotlari callback handleri"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return

        user_id = int(callback.data.split("_")[1])
        user_data = await db.get_user_data(user_id)

        if not user_data:
            await callback.answer("❌ Foydalanuvchi topilmadi!", show_alert=True)
            return

        user_info = user_data.user_info
        stats = user_data.stats
        messages = user_data.messages

        # So'nggi 3 ta xabarni olish
        recent_messages = messages[-3:] if len(messages) > 3 else messages
        recent_text = ""

        for msg in recent_messages:
            msg_type = "👤" if msg.type == "user" else "👨‍💻"
            msg_text = escape_html(msg.text[:50])
            if len(msg.text) > 50:
                msg_text += "..."
            recent_text += f"{msg_type} {msg.timestamp}: {msg_text}\n"

        info_text = f"""
👤 <b>Foydalanuvchi ma'lumotlari</b>

<b>Shaxsiy ma'lumotlar:</b>
• Ism: {escape_html(user_info.first_name)} {escape_html(user_info.last_name or '')}
• Username: @{user_info.username or 'Mavjud emas'}
• ID: <code>{user_info.id}</code>
• Birinchi murojaat: {user_info.first_contact}

    <b>Statistika:</b>
    • Jami xabarlar: {stats.total_messages}
    • So'nggi faollik: {stats.last_activity}
    • Status: {'🔴 Bloklangan' if user_info.is_blocked else '🟢 Faol'}

    <b>So'nggi xabarlar:</b>
    {recent_text or "Xabarlar yo'q"}
    """

        # Tugmalar
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="💬 Javob berish", callback_data=f"reply_{user_id}")

        if user_info.is_blocked:
            keyboard.button(text="✅ Blokdan chiqarish", callback_data=f"unblock_{user_id}")
        else:
            keyboard.button(text="🚫 Bloklash", callback_data=f"block_{user_id}")

        keyboard.adjust(2)

        await callback.message.answer(info_text, reply_markup=keyboard.as_markup())
        await callback.answer()

    except Exception as e:
        logger.error(f"User info callback xatoligi: {e}")
        await callback.answer("❌ Xatolik yuz berdi!")


@router.callback_query(F.data.startswith("block_"))
async def block_user_callback_handler(callback: CallbackQuery):
    """Foydalanuvchini bloklash callback handleri"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return

        user_id = int(callback.data.split("_")[1])

        if await db.block_user(user_id):
            await callback.answer("🚫 Foydalanuvchi bloklandi!", show_alert=True)
            logger.info(f"🚫 Foydalanuvchi bloklandi: {user_id}")
        else:
            await callback.answer("❌ Bloklashda xatolik!", show_alert=True)

    except Exception as e:
        logger.error(f"Block callback xatoligi: {e}")
        await callback.answer("❌ Xatolik yuz berdi!")


@router.callback_query(F.data.startswith("unblock_"))
async def unblock_user_callback_handler(callback: CallbackQuery):
    """Foydalanuvchini blokdan chiqarish callback handleri"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
            return

        user_id = int(callback.data.split("_")[1])

        if await db.unblock_user(user_id):
            await callback.answer("✅ Foydalanuvchi blokdan chiqarildi!", show_alert=True)
            logger.info(f"✅ Blokdan chiqarildi: {user_id}")
        else:
            await callback.answer("❌ Blokdan chiqarishda xatolik!", show_alert=True)

    except Exception as e:
        logger.error(f"Unblock callback xatoligi: {e}")
        await callback.answer("❌ Xatolik yuz berdi!")
