# 🤖 Telegram Support Bot

Foydalanuvchilar va admin o'rtasida aloqa o'rnatish uchun mo'ljallangan zamonaviy Telegram bot.

## ✨ Xususiyatlar

### 👥 Foydalanuvchilar uchun:
- 📝 Oddiy xabar yuborish
- ⚡ Tez javob olish
- 🔔 Javob haqida bildirishnoma

### 👨‍💻 Admin uchun:
- 📋 Barcha xabarlarni ko'rish
- 💬 Tez javob berish
- 📊 To'liq statistika
- 🔍 Xabarlarda qidirish
- 🚫 Foydalanuvchilarni bloklash
- 💾 Avtomatik zaxira
- 📱 Inline tugmalar bilan qulay boshqaruv

## 🛠 Texnologiyalar

- **Python 3.8+**
- **aiogram 3.8** - zamonaviy async Telegram bot framework
- **JSON** - ma'lumotlar saqlash
- **asyncio** - asinxron dasturlash

## 📦 O'rnatish

### 1. Repository ni clone qiling
```bash
git clone https://github.com/sizning-username/telegram-support-bot.git
cd telegram-support-bot
```

### 2. Virtual muhit yarating
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Kerakli kutubxonalarni o'rnating
```bash
pip install -r requirements.txt
```

### 4. Bot yaratish
1. [@BotFather](https://t.me/botfather)ga murojaat qiling
2. `/newbot` komandasi bilan yangi bot yarating
3. Bot tokenini oling

### 5. Admin ID olish
1. [@userinfobot](https://t.me/userinfobot)ga `/start` yuboring
2. O'z user ID'ingizni oling

### 6. Sozlamalar
```bash
# .env faylini yarating
cp .env.example .env

# .env faylini tahrirlang va o'z ma'lumotlaringizni kiriting
```

yoki `config.py` faylida to'g'ridan-to'g'ri o'zgartiring:
```python
BOT_TOKEN = "sizning_bot_tokeningiz"
ADMIN_ID = sizning_admin_id_si
```

### 7. Botni ishga tushiring
```bash
python main.py
```

## 📁 Loyiha tuzilishi

```
telegram-support-bot/
├── main.py              # Asosiy fayl
├── config.py            # Sozlamalar
├── handlers.py          # Bot handlerlari
├── database.py          # Ma'lumotlar bazasi
├── utils.py             # Yordamchi funksiyalar
├── requirements.txt     # Python kutubxonalari
├── .env.example         # Muhit o'zgaruvchilari misoli
├── README.md           # Bu fayl
├── data/               # Ma'lumotlar papkasi
│   └── messages.json   # Xabarlar bazasi
├── logs/               # Log fayllar
│   └── bot.log        # Bot loglari
└── backup/            # Zaxira fayllar
    └── messages_backup_*.json
```

## 🎯 Bot komandalar

### 👤 Oddiy foydalanuvchilar uchun:
- `/start` - Botni boshlash
- `/help` - Yordam

### 👨‍💻 Admin uchun:
- `/messages` - Barcha xabarlarni ko'rish
- `/stats` - Bot statistikasi
- `/reply <user_id> <xabar>` - Javob berish
- `/search <so'z>` - Xabarlarda qidirish
- `/backup` - Zaxira yaratish
- `/help` - Admin yordam

## 💡 Ishlatish misollari

### Javob berish:
```
/reply 123456789 Salom! Sizning savolingizga javob...
```

### Qidirish:
```
/search python
```

## 🔧 Sozlamalar

`config.py` faylida quyidagi sozlamalarni o'zgartirishingiz mumkin:

- `MAX_MESSAGE_LENGTH` - Maksimal xabar uzunligi
- `DAILY_MESSAGE_LIMIT` - Kunlik xabarlar cheklovi  
- `MIN_MESSAGE_INTERVAL` - Xabarlar orasidagi minimal vaqt
- `AUTO_BACKUP_HOURS` - Avtomatik zaxira vaqti

## 📊 Ma'lumotlar

Bot barcha ma'lumotlarni JSON formatda saqlaydi:
- Foydalanuvchi ma'lumotlari
- Barcha xabarlar
- Statistika
- Vaqt belgilari

## 🔒 Xavfsizlik

- Admin huquqlari tekshiriladi
- Foydalanuvchilarni bloklash imkoniyati
- Spam himoya mexanizmlari
- Xavfsiz HTML formatting

## 🚀 Kengaytirish imkoniyatlari

- PostgreSQL/MySQL bilan ishlash
- Fayl yuborish qo'llab-quvvatlash
- Webhook rejimi
- Ko'p tilli interfeys
- Bot analitika
- Ticket sistem

## 🐛 Xatoliklarni tuzatish

### Umumiy muammolar:

1. **Bot javob bermayapti**
   - Token to'g'riligini tekshiring
   - Internet aloqani tekshiring
   - Log fayllarni ko'ring

2. **Admin komandalar ishlamayapti**
   - Admin ID to'g'riligini tekshiring
   - Bot qaytadan ishga tushiring

3. **Ma'lumotlar saqlanmayapti**
   - `data/` papkasiga yozish huquqini tekshiring
   - Disk bo'sh joyini tekshiring

### Log fayllar:
```bash
tail -f logs/bot.log
```

## 🤝 Hissa qo'shish

1. Fork qiling
2. Yangi branch yarating (`git checkout -b yangi-xususiyat`)
3. O'zgartirishlarni commit qiling (`git commit -am 'Yangi xususiyat qo'shildi'`)
4. Branch'ni push qiling (`git push origin yangi-xususiyat`)
5. Pull Request yarating

## 📝 Litsenziya

MIT License - batafsil ma'lumot uchun LICENSE faylni ko'ring.

## 📞 Yordam

Savollar bo'lsa:
- Issue yarating
- Email: your-email@example.com
- Telegram: @your_username

## 🎉 Minnatdorchilik

- [aiogram](https://github.com/aiogram/aiogram) - ajoyib async Telegram bot framework
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - ilhom manbai

---

⭐ Agar loyiha foydali bo'lsa, star bosishni unutmang!