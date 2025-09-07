#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yordamchi funksiyalar (aiogram 3.8)
Umumiy ishlatish uchun funksiyalar
"""

import html
import re
import os
import mimetypes
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from config import ADMIN_ID, Settings, Formats, MediaTypes, Security


def is_admin(user_id: int) -> bool:
    """Foydalanuvchi admin ekanligini tekshirish"""
    return user_id == ADMIN_ID


def escape_html(text: str) -> str:
    """HTML belgilarini xavfsiz qilish"""
    if not text:
        return ""
    return html.escape(str(text))


def format_user_info(user) -> str:
    """Foydalanuvchi ma'lumotlarini formatlash"""
    name = f"{user.first_name} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else "Username yo'q"
    return f"{name} ({username}) | ID: {user.id}"


def split_long_message(text: str, max_length: int = Settings.MAX_MESSAGE_LENGTH) -> List[str]:
    """Uzun matnni qismlarga bo'lish"""
    if len(text) <= max_length:
        return [text]

    parts = []
    current_part = ""

    # Matnni qatorlarga bo'lish
    lines = text.split('\n')

    for line in lines:
        # Agar qator juda uzun bo'lsa
        if len(line) > max_length:
            # So'zlarga bo'lish
            words = line.split(' ')
            current_line = ""

            for word in words:
                if len(current_line) + len(word) + 1 <= max_length:
                    current_line += f" {word}" if current_line else word
                else:
                    if current_part:
                        if len(current_part) + len(current_line) + 1 <= max_length:
                            current_part += f"\n{current_line}"
                            current_line = word
                        else:
                            parts.append(current_part)
                            current_part = current_line
                            current_line = word
                    else:
                        current_part = current_line
                        current_line = word

            # Oxirgi qismni qo'shish
            if current_line:
                if current_part and len(current_part) + len(current_line) + 1 <= max_length:
                    current_part += f"\n{current_line}"
                elif current_part:
                    parts.append(current_part)
                    current_part = current_line
                else:
                    current_part = current_line
        else:
            # Qator normal uzunlikda
            if len(current_part) + len(line) + 1 <= max_length:
                current_part += f"\n{line}" if current_part else line
            else:
                if current_part:
                    parts.append(current_part)
                current_part = line

    # So'nggi qismni qo'shish
    if current_part:
        parts.append(current_part)

    return parts


def format_datetime(dt_str: str, format_type: str = "full") -> str:
    """Sana va vaqtni formatlash"""
    try:
        dt = datetime.strptime(dt_str, Formats.DATETIME_FORMAT)

        if format_type == "date":
            return dt.strftime(Formats.DATE_FORMAT)
        elif format_type == "time":
            return dt.strftime(Formats.TIME_FORMAT)
        elif format_type == "short":
            return dt.strftime("%d.%m %H:%M")
        else:  # full
            return dt.strftime("%d.%m.%Y %H:%M")
    except:
        return dt_str


def format_file_size(size_bytes: int) -> str:
    """Fayl hajmini formatlash"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def format_duration(seconds: int) -> str:
    """Davomiylikni formatlash (soniya)"""
    if not seconds:
        return "00:00"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def get_media_emoji(media_type: str) -> str:
    """Media turi uchun emoji olish"""
    return MediaTypes.MEDIA_EMOJIS.get(media_type, "📎")


def get_media_name(media_type: str) -> str:
    """Media turi nomini olish"""
    return MediaTypes.MEDIA_NAMES.get(media_type, "Media")


def is_safe_file(filename: str, mime_type: str = None) -> tuple[bool, str]:
    """Fayl xavfsizligini tekshirish"""
    if not filename:
        return False, "Fayl nomi yo'q"

    filename_lower = filename.lower()

    # APK va xavfli fayllarni tekshirish
    for blocked_type in Settings.BLOCKED_FILE_TYPES:
        if filename_lower.endswith(blocked_type):
            return False, f"{blocked_type.upper()} fayllari taqiqlangan!"

    # Xavfli patternlarni tekshirish
    for pattern in Security.DANGEROUS_PATTERNS:
        if re.match(pattern, filename_lower):
            return False, "Xavfli fayl turi!"

    # MIME type tekshirish
    if mime_type and mime_type in Security.BLOCKED_MIME_TYPES:
        return False, "Taqiqlangan fayl turi!"

    return True, ""


def validate_file_size(size_bytes: int) -> tuple[bool, str]:
    """Fayl hajmini tekshirish"""
    max_size_bytes = Settings.MAX_FILE_SIZE * 1024 * 1024

    if size_bytes > max_size_bytes:
        return False, f"Fayl juda katta! Maksimal hajm: {Settings.MAX_FILE_SIZE}MB"

    return True, ""


def clean_filename(filename: str) -> str:
    """Fayl nomini tozalash"""
    if not filename:
        return "unknown_file"

    # Xavfli belgilarni olib tashlash
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Uzunlikni cheklash
    if len(cleaned) > 100:
        name, ext = os.path.splitext(cleaned)
        cleaned = name[:95] + ext

    return cleaned


def get_file_info(file_obj) -> Dict[str, Any]:
    """Fayl ma'lumotlarini olish"""
    info = {
        "file_id": file_obj.file_id,
        "file_unique_id": getattr(file_obj, 'file_unique_id', ''),
        "file_size": getattr(file_obj, 'file_size', 0),
        "file_name": getattr(file_obj, 'file_name', ''),
        "mime_type": getattr(file_obj, 'mime_type', ''),
    }

    # Qo'shimcha ma'lumotlar
    if hasattr(file_obj, 'width') and hasattr(file_obj, 'height'):
        info['dimensions'] = f"{file_obj.width}x{file_obj.height}"

    if hasattr(file_obj, 'duration'):
        info['duration'] = file_obj.duration
        info['duration_formatted'] = format_duration(file_obj.duration or 0)

    if hasattr(file_obj, 'title'):
        info['title'] = file_obj.title or 'Noma\'lum'

    if hasattr(file_obj, 'performer'):
        info['performer'] = file_obj.performer or 'Noma\'lum'

    return info


def create_media_summary(media_type: str, file_info: Dict[str, Any], caption: str = None) -> str:
    """Media xabar xulosasi yaratish"""
    emoji = get_media_emoji(media_type)
    name = get_media_name(media_type)

    summary = f"{emoji} {name}"

    if file_info.get('file_size'):
        summary += f"\n• Hajmi: {format_file_size(file_info['file_size'])}"

    if file_info.get('duration_formatted'):
        summary += f"\n• Davomiyligi: {file_info['duration_formatted']}"

    if file_info.get('dimensions'):
        summary += f"\n• O'lchami: {file_info['dimensions']}"

    if file_info.get('file_name'):
        summary += f"\n• Nomi: {file_info['file_name']}"

    if file_info.get('title') and file_info['title'] != 'Noma\'lum':
        summary += f"\n• Sarlavha: {file_info['title']}"

    if file_info.get('performer') and file_info['performer'] != 'Noma\'lum':
        summary += f"\n• Ijrochi: {file_info['performer']}"

    summary += f"\n• File ID: {file_info['file_id']}"

    if caption:
        summary += f"\n\n📝 Izoh: {caption}"

    return summary


def extract_media_text(media_type: str, file_obj, caption: str = None) -> str:
    """Media obyektidan matn yaratish"""
    file_info = get_file_info(file_obj)
    return create_media_summary(media_type, file_info, caption)


def validate_user_input(text: str) -> tuple[bool, str]:
    """Foydalanuvchi kiritgan matnni tekshirish"""
    if not text or not text.strip():
        return False, "Bo'sh xabar yuborib bo'lmaydi!"

    # Uzunlikni tekshirish
    if len(text) > 4000:
        return False, "Xabar juda uzun! Maksimal 4000 belgi."

    # Spam tekshirish
    spam_patterns = [
        r'(.)\1{10,}',  # Bir xil belgining 10 martadan ko'p takrorlanishi
        r'[A-Z]{50,}',  # 50 dan ko'p katta harf
        r'(https?://[^\s]+){5,}',  # 5 dan ko'p link
    ]

    for pattern in spam_patterns:
        if re.search(pattern, text):
            return False, "Xabar spam kabi ko'rinadi!"

    return True, ""


def get_message_stats(messages: list) -> dict:
    """Xabarlar statistikasi"""
    if not messages:
        return {
            'total': 0,
            'user_messages': 0,
            'admin_replies': 0,
            'media_messages': 0,
            'text_messages': 0,
            'avg_length': 0,
            'last_message_time': None
        }

    user_messages = [m for m in messages if m.type == "user"]
    admin_replies = [m for m in messages if m.type == "admin"]

    # Media va matn xabarlarini ajratish
    media_messages = []
    text_messages = []

    for msg in user_messages:
        if any(media_type in msg.text.lower() for media_type in MediaTypes.MEDIA_NAMES.values()):
            media_messages.append(msg)
        else:
            text_messages.append(msg)

    total_length = sum(len(m.text) for m in messages)
    avg_length = total_length // len(messages) if messages else 0

    last_message = max(messages, key=lambda x: x.timestamp) if messages else None

    return {
        'total': len(messages),
        'user_messages': len(user_messages),
        'admin_replies': len(admin_replies),
        'media_messages': len(media_messages),
        'text_messages': len(text_messages),
        'avg_length': avg_length,
        'last_message_time': last_message.timestamp if last_message else None
    }


def create_pagination_keyboard(items: list, page: int = 1, per_page: int = 10, callback_prefix: str = "page"):
    """Sahifalash uchun keyboard yaratish"""
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    total_pages = (len(items) + per_page - 1) // per_page

    keyboard = InlineKeyboardBuilder()

    # Sahifa tugmalari
    if total_pages > 1:
        buttons = []

        if page > 1:
            buttons.append(("⬅️ Oldingi", f"{callback_prefix}_{page - 1}"))

        buttons.append((f"{page}/{total_pages}", "current_page"))

        if page < total_pages:
            buttons.append(("Keyingi ➡️", f"{callback_prefix}_{page + 1}"))

        for text, data in buttons:
            keyboard.button(text=text, callback_data=data)

        keyboard.adjust(len(buttons))

    return keyboard


def extract_user_id_from_message(text: str) -> Optional[int]:
    """Xabardan user ID ni ajratib olish"""
    # /reply 123456789 xabar formatidan user ID ni olish
    match = re.search(r'/reply\s+(\d+)', text)
    if match:
        return int(match.group(1))

    # Boshqa formatlar
    match = re.search(r'ID:\s*(\d+)', text)
    if match:
        return int(match.group(1))

    return None


def generate_media_report(stats: dict, users_data: dict) -> str:
    """Media hisobot generatsiya qilish"""
    report_time = datetime.now().strftime(Formats.DATETIME_FORMAT)

    # Media statistikasini hisoblash
    total_media = 0
    media_types_count = {}

    for user_data in users_data.values():
        user_stats = get_message_stats(user_data.messages)
        total_media += user_stats['media_messages']

    report = f"""
📊 <b>Bot Media Hisoboti</b>
📅 {report_time}

📈 <b>Umumiy ko'rsatkichlar:</b>
• Jami foydalanuvchilar: {stats['total_users']}
• Jami xabarlar: {stats['total_messages']}
• Media xabarlar: {total_media}
• Matn xabarlar: {stats['total_messages'] - total_media}

💬 <b>Xabarlar taqsimoti:</b>
• Javob kutayotgan: {stats['unread_messages']}
• Faol foydalanuvchilar: {stats['active_users_24h']}

🏆 <b>Eng faol foydalanuvchilar:</b>
"""

    # Top foydalanuvchilarni qo'shish
    for i, top_user in enumerate(stats['top_users'][:5], 1):
        report += f"{i}. {escape_html(top_user['name'])} - {top_user['messages_count']} xabar\n"

    return report


def sanitize_filename(filename: str) -> str:
    """Fayl nomini xavfsiz qilish"""
    # Taqiqlangan belgilarni olib tashlash
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Uzunlikni cheklash
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:95] + ('.' + ext if ext else '')

    return filename


def is_valid_user_id(user_id_str: str) -> bool:
    """User ID to'g'riligini tekshirish"""
    try:
        user_id = int(user_id_str)
        # Telegram user ID 1 dan 2147483647 gacha
        return 1 <= user_id <= 2147483647
    except (ValueError, TypeError):
        return False


def get_mime_type(filename: str) -> str:
    """Fayl nomidan MIME type ni aniqlash"""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'


def is_image_file(filename: str) -> bool:
    """Rasm fayli ekanligini tekshirish"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    return any(filename.lower().endswith(ext) for ext in image_extensions)


def is_video_file(filename: str) -> bool:
    """Video fayli ekanligini tekshirish"""
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']
    return any(filename.lower().endswith(ext) for ext in video_extensions)


def is_audio_file(filename: str) -> bool:
    """Audio fayli ekanligini tekshirish"""
    audio_extensions = ['.mp3', '.wav', '.flac', '.ogg', '.aac', '.m4a']
    return any(filename.lower().endswith(ext) for ext in audio_extensions)


def create_file_path(media_dir: Path, user_id: int, filename: str) -> Path:
    """Fayl yo'lini yaratish"""
    user_dir = media_dir / str(user_id)
    user_dir.mkdir(exist_ok=True)

    # Fayl nomini xavfsiz qilish
    safe_filename = sanitize_filename(filename)

    # Agar fayl mavjud bo'lsa, yangi nom berish
    file_path = user_dir / safe_filename
    counter = 1

    while file_path.exists():
        name, ext = os.path.splitext(safe_filename)
        file_path = user_dir / f"{name}_{counter}{ext}"
        counter += 1

    return file_path


def get_time_ago(timestamp_str: str) -> str:
    """Vaqt farqini hisoblash"""
    try:
        timestamp = datetime.strptime(timestamp_str, Formats.DATETIME_FORMAT)
        now = datetime.now()
        diff = now - timestamp

        if diff.days > 0:
            return f"{diff.days} kun oldin"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} soat oldin"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} daqiqa oldin"
        else:
            return "Hozir"
    except:
        return timestamp_str


def mask_sensitive_data(text: str) -> str:
    """Maxfiy ma'lumotlarni yashirish"""
    # Telefon raqamlar
    text = re.sub(r'\+?[1-9]\d{1,14}', '*' * 10, text)

    # Email
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***', text)

    # Kart raqamlar
    text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '**** **** **** ****', text)

    return text


class TextFormatter:
    """Matn formatlash uchun klass"""

    @staticmethod
    def bold(text: str) -> str:
        return f"<b>{escape_html(text)}</b>"

    @staticmethod
    def italic(text: str) -> str:
        return f"<i>{escape_html(text)}</i>"

    @staticmethod
    def code(text: str) -> str:
        return f"<code>{escape_html(text)}</code>"

    @staticmethod
    def pre(text: str) -> str:
        return f"<pre>{escape_html(text)}</pre>"

    @staticmethod
    def link(url: str, text: str) -> str:
        return f'<a href="{url}">{escape_html(text)}</a>'

    @staticmethod
    def user_link(user_id: int, name: str) -> str:
        return f'<a href="tg://user?id={user_id}">{escape_html(name)}</a>'


# Global formatter instance
fmt = TextFormatter()