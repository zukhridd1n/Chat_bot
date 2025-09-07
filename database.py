#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ma'lumotlar bazasi moduli (aiogram 3.8)
Foydalanuvchi xabarlarini saqlash va boshqarish
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict

from config import MESSAGES_FILE, Settings, Formats

logger = logging.getLogger(__name__)


@dataclass
class UserInfo:
    """Foydalanuvchi ma'lumotlari"""
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    first_contact: str = ""
    is_blocked: bool = False


@dataclass
class Message:
    """Xabar ma'lumotlari"""
    text: str
    timestamp: str
    type: str  # "user" yoki "admin"
    message_id: Optional[int] = None


@dataclass
class UserStats:
    """Foydalanuvchi statistikasi"""
    total_messages: int = 0
    last_message: str = ""
    last_activity: str = ""
    is_active_today: bool = False


@dataclass
class UserData:
    """Foydalanuvchi to'liq ma'lumotlari"""
    user_info: UserInfo
    messages: List[Message]
    stats: UserStats


class MessageDatabase:
    """Xabarlar bazasini boshqarish uchun sinf"""

    def __init__(self, file_path: Path = MESSAGES_FILE):
        """Ma'lumotlar bazasini ishga tushirish"""
        self.file_path = file_path
        self._lock = asyncio.Lock()
        self._ensure_data_directory()
        self.data: Dict[str, UserData] = {}
        self._loaded = False
        # asyncio.create_task() ni olib tashladik

    def _ensure_data_directory(self):
        """Data papkasini yaratish"""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    async def _ensure_loaded(self):
        """Ma'lumotlarni lazy loading bilan yuklash"""
        if not self._loaded:
            await self._load_data()
            self._loaded = True

    async def _load_data(self):
        """Ma'lumotlarni async yuklash"""
        try:
            if self.file_path.exists():
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)

                # Ma'lumotlarni dataclass'larga o'girish
                for user_id, user_data in raw_data.items():
                    try:
                        # UserInfo yaratish
                        user_info_dict = user_data.get("user_info", {})
                        user_info = UserInfo(**user_info_dict)

                        # Messages yaratish
                        messages_list = []
                        for msg_data in user_data.get("messages", []):
                            message = Message(**msg_data)
                            messages_list.append(message)

                        # UserStats yaratish
                        stats_dict = user_data.get("stats", {})
                        stats = UserStats(**stats_dict)

                        # UserData yaratish
                        self.data[user_id] = UserData(
                            user_info=user_info,
                            messages=messages_list,
                            stats=stats
                        )
                    except Exception as e:
                        logger.error(f"Foydalanuvchi {user_id} ma'lumotlarini yuklashda xatolik: {e}")

                logger.info(f"📂 {len(self.data)} foydalanuvchi ma'lumoti yuklandi")
            else:
                logger.info("🆕 Yangi ma'lumotlar bazasi yaratildi")

        except Exception as e:
            logger.error(f"Ma'lumotlarni yuklashda xatolik: {e}")

    async def _save_data(self) -> bool:
        """Ma'lumotlarni async saqlash"""
        async with self._lock:
            try:
                # Dataclass'larni dict'ga o'girish
                raw_data = {}
                for user_id, user_data in self.data.items():
                    raw_data[user_id] = {
                        "user_info": asdict(user_data.user_info),
                        "messages": [asdict(msg) for msg in user_data.messages],
                        "stats": asdict(user_data.stats)
                    }

                # Faylga yozish
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(raw_data, f, ensure_ascii=False, indent=2)

                logger.debug("💾 Ma'lumotlar saqlandi")
                return True

            except Exception as e:
                logger.error(f"Ma'lumotlarni saqlashda xatolik: {e}")
                return False

    async def add_user_message(self, user_id: int, user_dict: Dict[str, Any], message_text: str,
                               message_id: int = None) -> bool:
        """Foydalanuvchi xabarini qo'shish"""
        await self._ensure_loaded()  # Lazy loading

        try:
            user_id_str = str(user_id)
            timestamp = datetime.now().strftime(Formats.DATETIME_FORMAT)

            # Yangi foydalanuvchini yaratish
            if user_id_str not in self.data:
                user_info = UserInfo(
                    id=user_id,
                    first_name=user_dict.get("first_name", ""),
                    last_name=user_dict.get("last_name"),
                    username=user_dict.get("username"),
                    first_contact=timestamp
                )

                user_stats = UserStats(
                    total_messages=0,
                    last_message=timestamp,
                    last_activity=timestamp,
                    is_active_today=True
                )

                self.data[user_id_str] = UserData(
                    user_info=user_info,
                    messages=[],
                    stats=user_stats
                )

                logger.info(f"👤 Yangi foydalanuvchi: {user_dict.get('first_name')} ({user_id})")

            # Xabarni qo'shish
            message = Message(
                text=message_text,
                timestamp=timestamp,
                type="user",
                message_id=message_id
            )

            self.data[user_id_str].messages.append(message)

            # Statistikani yangilash
            self.data[user_id_str].stats.total_messages += 1
            self.data[user_id_str].stats.last_message = timestamp
            self.data[user_id_str].stats.last_activity = timestamp
            self.data[user_id_str].stats.is_active_today = True

            # Foydalanuvchi ma'lumotlarini yangilash
            self.data[user_id_str].user_info.first_name = user_dict.get("first_name", "")
            self.data[user_id_str].user_info.last_name = user_dict.get("last_name")
            self.data[user_id_str].user_info.username = user_dict.get("username")

            return await self._save_data()

        except Exception as e:
            logger.error(f"Xabar qo'shishda xatolik: {e}")
            return False

    async def add_admin_reply(self, user_id: int, reply_text: str) -> bool:
        """Admin javobini qo'shish"""
        await self._ensure_loaded()  # Lazy loading

        try:
            user_id_str = str(user_id)
            timestamp = datetime.now().strftime(Formats.DATETIME_FORMAT)

            if user_id_str in self.data:
                message = Message(
                    text=reply_text,
                    timestamp=timestamp,
                    type="admin"
                )

                self.data[user_id_str].messages.append(message)
                return await self._save_data()
            else:
                logger.error(f"Foydalanuvchi topilmadi: {user_id}")
                return False

        except Exception as e:
            logger.error(f"Admin javobini qo'shishda xatolik: {e}")
            return False

    async def get_all_users(self) -> Dict[str, UserData]:
        """Barcha foydalanuvchilarni olish"""
        await self._ensure_loaded()  # Lazy loading
        return self.data.copy()

    async def get_user_data(self, user_id: int) -> Optional[UserData]:
        """Foydalanuvchi ma'lumotlarini olish"""
        await self._ensure_loaded()  # Lazy loading
        return self.data.get(str(user_id))

    async def get_user_messages(self, user_id: int) -> List[Message]:
        """Foydalanuvchi xabarlarini olish"""
        user_data = await self.get_user_data(user_id)
        return user_data.messages if user_data else []

    async def get_unread_messages_count(self) -> int:
        """Javob berilmagan xabarlar soni"""
        await self._ensure_loaded()  # Lazy loading
        count = 0
        for user_data in self.data.values():
            if user_data.messages and user_data.messages[-1].type == "user":
                count += 1
        return count

    async def get_stats(self) -> Dict[str, Any]:
        """Bot statistikasi"""
        await self._ensure_loaded()  # Lazy loading

        total_users = len(self.data)
        total_messages = sum(len(user_data.messages) for user_data in self.data.values())
        unread_messages = await self.get_unread_messages_count()

        # Faol foydalanuvchilar (24 soat)
        yesterday = datetime.now() - timedelta(days=1)
        active_users = 0

        for user_data in self.data.values():
            try:
                last_activity = datetime.strptime(
                    user_data.stats.last_activity,
                    Formats.DATETIME_FORMAT
                )
                if last_activity > yesterday:
                    active_users += 1
            except (ValueError, AttributeError):
                pass

        # Eng faol foydalanuvchilar
        top_users = sorted(
            self.data.items(),
            key=lambda x: x[1].stats.total_messages,
            reverse=True
        )[:5]

        return {
            "total_users": total_users,
            "total_messages": total_messages,
            "unread_messages": unread_messages,
            "active_users_24h": active_users,
            "top_users": [
                {
                    "user_id": user_id,
                    "name": f"{data.user_info.first_name} {data.user_info.last_name or ''}".strip(),
                    "messages_count": data.stats.total_messages
                }
                for user_id, data in top_users
            ]
        }

    async def search_messages(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Xabarlarda qidirish"""
        await self._ensure_loaded()  # Lazy loading

        results = []
        query_lower = query.lower()

        for user_id, user_data in self.data.items():
            user_info = user_data.user_info

            for message in user_data.messages:
                if query_lower in message.text.lower():
                    results.append({
                        "user_id": user_id,
                        "user_name": f"{user_info.first_name} {user_info.last_name or ''}".strip(),
                        "username": user_info.username,
                        "message": message,
                        "match_text": message.text
                    })

                    if len(results) >= limit:
                        break

            if len(results) >= limit:
                break

        return results

    async def backup_data(self, backup_path: Path = None) -> bool:
        """Ma'lumotlarni zahiralash"""
        await self._ensure_loaded()  # Lazy loading

        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.file_path.parent.parent / "backup" / f"messages_backup_{timestamp}.json"

            # Backup papkasini yaratish
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # Ma'lumotlarni nusxalash
            raw_data = {}
            for user_id, user_data in self.data.items():
                raw_data[user_id] = {
                    "user_info": asdict(user_data.user_info),
                    "messages": [asdict(msg) for msg in user_data.messages],
                    "stats": asdict(user_data.stats)
                }

            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, ensure_ascii=False, indent=2)

            logger.info(f"💾 Zahira nusxa yaratildi: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Zahira yaratishda xatolik: {e}")
            return False

    async def block_user(self, user_id: int) -> bool:
        """Foydalanuvchini bloklash"""
        try:
            user_data = await self.get_user_data(user_id)
            if user_data:
                user_data.user_info.is_blocked = True
                return await self._save_data()
            return False
        except Exception as e:
            logger.error(f"Foydalanuvchini bloklashda xatolik: {e}")
            return False

    async def unblock_user(self, user_id: int) -> bool:
        """Foydalanuvchini blokdan chiqarish"""
        try:
            user_data = await self.get_user_data(user_id)
            if user_data:
                user_data.user_info.is_blocked = False
                return await self._save_data()
            return False
        except Exception as e:
            logger.error(f"Blokdan chiqarishda xatolik: {e}")
            return False

    async def is_user_blocked(self, user_id: int) -> bool:
        """Foydalanuvchi bloklanganmi tekshirish"""
        user_data = await self.get_user_data(user_id)
        return user_data.user_info.is_blocked if user_data else False


# Global database instance
db = MessageDatabase()