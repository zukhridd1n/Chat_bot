#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot sozlamalari (aiogram 3.8)
Bu faylda barcha muhim sozlamalar saqlanadi
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# =============================================================================
# BOT SOZLAMALARI
# =============================================================================

# Bot tokeni - @BotFather'dan olinadi
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Admin foydalanuvchi ID'si - @userinfobot'dan olinadi
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

# =============================================================================
# PAPKALAR VA FAYLLAR
# =============================================================================

# Asosiy papka
BASE_DIR = Path(__file__).parent

# Data papkasi
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Logs papkasi
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Backup papkasi
BACKUP_DIR = BASE_DIR / "backup"
BACKUP_DIR.mkdir(exist_ok=True)

# Media papkasi
MEDIA_DIR = BASE_DIR / "media"
MEDIA_DIR.mkdir(exist_ok=True)

# Fayllar
MESSAGES_FILE = DATA_DIR / "messages.json"
LOG_FILE = LOGS_DIR / "bot.log"


# =============================================================================
# MATN SOZLAMALARI
# =============================================================================

class Messages:
    """Bot xabarlari"""

    # Start komandasi - oddiy foydalanuvchilar uchun
    START = """
🤖 <b>Assalom aleykum!</b>

Men Xodimun shaxsiy bot-yordamchisiman.

📝 <b>Qanday ishlatish:</b>
• Menga savol, xabar yoki fayl yuboring
• Rasm, video, audio, hujjat - hammasi qabul qilinadi
• Xodimun sizning xabaringizni ko'radi
• Tez orada javob olasiz

📎 <b>Qo'llab-quvvatlanadigan fayllar:</b>
• 🖼️ Rasmlar (JPG, PNG, GIF)
• 🎥 Videolar va Video xabarlar
• 🎵 Audio va Ovozli xabarlar
• 📄 Hujjatlar (PDF, DOC, TXT, va boshqalar)
• 😄 Stikerlar va GIF animatsiyalar
• 📍 Joylashuv va Kontaktlar
• 📊 So'rovnomalar

🚫 <b>Taqiqlangan:</b> Faqat APK fayllari

🆘 Yordam kerak bo'lsa: /help

"""

    # Start komandasi - admin uchun
    START_ADMIN = """
🔧 <b>Admin Panel - Xush kelibsiz!</b>

Siz bot administratorisiz va to'liq nazoratga egasiz.

⚡ <b>Tezkor komandalar:</b>
• /messages - Barcha xabarlarni ko'rish
• /stats - Bot statistikasi
• /backup - Ma'lumotlar zaxirasi
• /help - To'liq yordam

💬 <b>Javob berish:</b>
<code>/reply &lt;user_id&gt; &lt;xabar&gt;</code>

🔍 <b>Qidirish:</b>
<code>/search &lt;kalit so'z&gt;</code>

📊 <b>Hozirgi holat:</b>
• Bot faol va barcha media turlarini qabul qiladi
• APK fayllari avtomatik bloklangan
• Spam himoyasi yoqilgan

🚀 <b>Yangi funksiyalar:</b>
• Media fayllar to'liq qo'llab-quvvatlanadi
• File ID va batafsil ma'lumotlar ko'rsatiladi
• Foydalanuvchilarni bloklash/blokdan chiqarish
• Avtomatik zaxira yaratish

💡 Bot to'liq ishga tayyor!
"""

    # Help - oddiy foydalanuvchi
    HELP_USER = """
📚 <b>Yordam bo'limi</b>

🔹 <b>Bot qanday ishlaydi:</b>
1️⃣ Menga savolingizni yoki faylingizni yuboring
2️⃣ Xodimun sizning xabaringizni ko'radi  
3️⃣ Xodimun sizga javob yuboradi

🔹 <b>Komandalar:</b>
• <code>/start</code> - Botni qayta boshlash
• <code>/help</code> - Bu yordam sahifasi

📎 <b>Media qo'llab-quvvatlash:</b>
• 🖼️ Rasmlar va GIF'lar
• 🎥 Video fayllar
• 🎵 Audio va musiqa
• 🎤 Ovozli xabarlar
• 🎬 Video xabarlar (dumaloq)
• 📄 Har qanday hujjatlar (APK bundan mustasno)
• 😄 Stikerlar
• 📍 Joylashuv
• 📞 Kontaktlar
• 📊 So'rovnomalar
• 🎲 O'yinlar (zar, nishon va h.k.)

💡 <b>Maslahat:</b> 
Fayl bilan birga izoh ham yozishingiz mumkin!

❓ <b>Savol-javob vaqti:</b> Odatda 1-24 soat ichida
"""

    # Help - admin
    HELP_ADMIN = """
🔧 <b>Admin Panel - Yordam</b>

🔹 <b>Admin komandalar:</b>
• <code>/messages</code> - Barcha xabarlarni ko'rish
• <code>/stats</code> - Bot statistikasi
• <code>/reply &lt;user_id&gt; &lt;xabar&gt;</code> - Javob berish
• <code>/search &lt;so'z&gt;</code> - Xabarlarda qidirish
• <code>/backup</code> - Ma'lumotlar zaxirasi

🔹 <b>Javob berish misoli:</b>
<code>/reply 123456789 Salom! Sizning savolingizga javob...</code>

📎 <b>Media xabarlar:</b>
• Barcha media turlari qo'llab-quvvatlanadi
• File ID ma'lumotlari admin xabarida ko'rsatiladi
• Media fayllarni yuklash uchun Telegram Bot API ishlatiladi

💡 <b>Maslahat:</b> 
Javob berishda doim mehribon va professional bo'ling!
"""

    # Xabar qabul qilindi
    MESSAGE_RECEIVED = """
✅ <b>Xabaringiz qabul qilindi!</b>

📝 Sizning xabaringiz (matn yoki media) Xodimun ko'rishiga yuborildi
⏰ Javob vaqti: odatda 1-24 soat ichida
🔔 Javob kelganda bildirishnoma olasiz

🙏 Sabr qilganingiz uchun rahmat!
"""

    # Admin bildirish
    @staticmethod
    def admin_notification(user, message_text, timestamp, user_id):
        return f"""
🔔 <b>Yangi xabar keldi!</b>

👤 <b>Foydalanuvchi:</b>
• Ism: {user.first_name} {user.last_name or ''}
• Username: @{user.username or 'Mavjud emas'}
• ID: <code>{user.id}</code>
• Vaqt: {timestamp}

💬 <b>Xabar:</b>
{message_text}

📤 <b>Javob berish:</b>
<code>/reply {user.id} </code>

---
💡 Tez javob bering, foydalanuvchi kutmoqda!
"""

    # Media admin bildirish
    @staticmethod
    def admin_media_notification(user, media_info, caption, timestamp, user_id, media_type):
        return f"""
🔔 <b>Yangi {media_type.upper()} xabar keldi!</b>

👤 <b>Foydalanuvchi:</b>
• Ism: {user.first_name} {user.last_name or ''}
• Username: @{user.username or 'Mavjud emas'}
• ID: <code>{user.id}</code>
• Vaqt: {timestamp}

📎 <b>Media ma'lumotlari:</b>
{media_info}

💬 <b>Izoh:</b>
{caption or 'Izoh yo\'q'}

📤 <b>Javob berish:</b>
<code>/reply {user.id} </code>

---
💡 Media faylni yuklash uchun file_id dan foydalaning!
"""


class Errors:
    """Xatolik xabarlari"""

    ADMIN_ONLY = "❌ Bu komanda faqat admin uchun!"
    NO_MESSAGES = "📭 Hozircha xabarlar mavjud emas"
    INVALID_REPLY_FORMAT = """
❌ <b>Noto'g'ri format!</b>

✅ <b>To'g'ri format:</b>
<code>/reply &lt;user_id&gt; &lt;xabar&gt;</code>

📝 <b>Misol:</b>
<code>/reply 123456789 Salom, sizning savolingizga javob...</code>
"""
    INVALID_USER_ID = "❌ User ID noto'g'ri! Raqam bo'lishi kerak."
    USER_NOT_FOUND = "❌ Bunday foydalanuvchi topilmadi!"
    REPLY_SUCCESS = "✅ Javob muvaffaqiyatli yuborildi!"
    REPLY_ERROR = "❌ Javob yuborishda xatolik yuz berdi!"
    GENERAL_ERROR = "❌ Kutilmagan xatolik yuz berdi!"
    NO_SEARCH_RESULTS = "🔍 Qidiruv natijasi topilmadi"
    BACKUP_SUCCESS = "💾 Ma'lumotlar zaxirasi yaratildi!"
    BACKUP_ERROR = "❌ Zaxira yaratishda xatolik!"

    # Media xatoliklari
    FILE_TOO_LARGE = "❌ Fayl juda katta! Maksimal hajm: {max_size}MB"
    INVALID_FILE_TYPE = "❌ Bu fayl turi ruxsat etilmagan!"
    APK_FILE_BLOCKED = "🚫 APK fayllari yuborish taqiqlangan!"
    MEDIA_PROCESSING_ERROR = "❌ Media faylni qayta ishlashda xatolik!"
    DOWNLOAD_ERROR = "❌ Faylni yuklashda xatolik!"


# =============================================================================
# BOT SOZLAMALARI
# =============================================================================

class Settings:
    """Bot sozlamalari"""

    # Debug rejimi
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # Log darajasi
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Maksimal xabar uzunligi
    MAX_MESSAGE_LENGTH = 4000

    # Kuniga maksimal xabarlar soni
    DAILY_MESSAGE_LIMIT = 50

    # Spam himoya - minimum vaqt (soniya)
    MIN_MESSAGE_INTERVAL = 5

    # Media sozlamalari
    # Ruxsat etilgan fayl turlari
    ALLOWED_FILE_TYPES = [
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',  # Rasmlar
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv',  # Videolar
        '.mp3', '.wav', '.flac', '.ogg', '.aac', '.m4a',  # Audio
        '.pdf', '.doc', '.docx', '.txt', '.rtf',  # Hujjatlar
        '.xls', '.xlsx', '.ppt', '.pptx',  # Office
        '.zip', '.rar', '.7z', '.tar', '.gz',  # Arxivlar
        '.json', '.xml', '.csv', '.sql'  # Ma'lumotlar
    ]

    # Taqiqlangan fayl turlari
    BLOCKED_FILE_TYPES = ['.apk', '.exe', '.msi', '.deb', '.rpm', '.dmg']

    # Maksimal fayl hajmi (MB)
    MAX_FILE_SIZE = 50

    # Auto backup vaqti (soat)
    AUTO_BACKUP_HOURS = 24

    # Media papka sozlamalari
    SAVE_MEDIA_FILES = os.getenv("SAVE_MEDIA_FILES", "False").lower() == "true"
    MAX_MEDIA_STORAGE = 500  # MB


# =============================================================================
# MEDIA TYPES
# =============================================================================

class MediaTypes:
    """Media turlari"""

    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE = "voice"
    VIDEO_NOTE = "video_note"
    DOCUMENT = "document"
    STICKER = "sticker"
    ANIMATION = "animation"
    LOCATION = "location"
    VENUE = "venue"
    CONTACT = "contact"
    POLL = "poll"
    DICE = "dice"

    # Media emojilari
    MEDIA_EMOJIS = {
        PHOTO: "📷",
        VIDEO: "🎥",
        AUDIO: "🎵",
        VOICE: "🎤",
        VIDEO_NOTE: "🎬",
        DOCUMENT: "📄",
        STICKER: "😄",
        ANIMATION: "🎭",
        LOCATION: "📍",
        VENUE: "🏢",
        CONTACT: "📞",
        POLL: "📊",
        DICE: "🎲"
    }

    # Media nomlari
    MEDIA_NAMES = {
        PHOTO: "Rasm",
        VIDEO: "Video",
        AUDIO: "Audio",
        VOICE: "Ovozli xabar",
        VIDEO_NOTE: "Video xabar",
        DOCUMENT: "Hujjat",
        STICKER: "Stiker",
        ANIMATION: "GIF",
        LOCATION: "Joylashuv",
        VENUE: "Joy",
        CONTACT: "Kontakt",
        POLL: "So'rovnoma",
        DICE: "O'yin"
    }


# =============================================================================
# CALLBACK DATA
# =============================================================================

class CallbackData:
    """Callback ma'lumotlari"""

    # Admin paneli
    ADMIN_MESSAGES = "admin_messages"
    ADMIN_STATS = "admin_stats"
    ADMIN_USERS = "admin_users"

    # Xabar boshqaruvi
    VIEW_USER = "view_user_{user_id}"
    REPLY_USER = "reply_user_{user_id}"
    BLOCK_USER = "block_user_{user_id}"
    DOWNLOAD_MEDIA = "download_{media_type}_{user_id}"

    # Navigatsiya
    NEXT_PAGE = "next_{page}"
    PREV_PAGE = "prev_{page}"
    BACK = "back"


# =============================================================================
# FORMATLAR
# =============================================================================

class Formats:
    """Matn formatlari"""

    # Sana formati
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M"

    # Foydalanuvchi formati
    USER_FORMAT = "{first_name} {last_name}"
    USER_INFO = "👤 {name} (@{username}) | ID: {user_id}"

    # Media formatlari
    MEDIA_INFO = "{emoji} {name}\n• Hajmi: {size}\n• File ID: {file_id}"
    AUDIO_INFO = "🎵 {title} - {performer}\n• Davomiyligi: {duration}\n• Hajmi: {size}"
    VIDEO_INFO = "🎥 Video\n• Davomiyligi: {duration}\n• O'lchami: {resolution}\n• Hajmi: {size}"


# =============================================================================
# XAVFSIZLIK SOZLAMALARI
# =============================================================================

class Security:
    """Xavfsizlik sozlamalari"""

    # Spam himoya
    MAX_MESSAGES_PER_MINUTE = 5
    MAX_IDENTICAL_MESSAGES = 3

    # Fayl xavfsizligi
    SCAN_FILES = True
    QUARANTINE_SUSPICIOUS = True

    # Taqiqlangan MIME turlari
    BLOCKED_MIME_TYPES = [
        'application/vnd.android.package-archive',  # APK
        'application/x-msdownload',  # EXE
        'application/x-msi',  # MSI
        'application/x-deb',  # DEB
        'application/x-rpm',  # RPM
        'application/x-apple-diskimage'  # DMG
    ]

    # Xavfli fayl nomlari patternlari
    DANGEROUS_PATTERNS = [
        r'.*\.apk$',
        r'.*\.exe$',
        r'.*\.msi$',
        r'.*\.scr$',
        r'.*\.bat$',
        r'.*\.cmd$',
        r'.*\.com$',
        r'.*\.pif$'
    ]