"""
مدیریت دیتابیس SQLite
"""

import aiosqlite
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

DATABASE_PATH = "war_game.db"


async def init_database():
    """ایجاد جداول دیتابیس"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # جدول بازیکنان
        await db.execute("""
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                country_name TEXT,
                money INTEGER DEFAULT 2000000,
                treasury INTEGER DEFAULT 0,
                military_power INTEGER DEFAULT 0,
                defense_power INTEGER DEFAULT 100,
                score INTEGER DEFAULT 0,
                weekly_score INTEGER DEFAULT 0,
                invite_code TEXT UNIQUE,
                invited_by INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_military_aid TEXT,
                military_aid_count INTEGER DEFAULT 0
            )
        """)
        
        # جدول کلن‌ها
        await db.execute("""
            CREATE TABLE IF NOT EXISTS clans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                leader_id INTEGER,
                treasury INTEGER DEFAULT 0,
                max_members INTEGER DEFAULT 5,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (leader_id) REFERENCES players(user_id)
            )
        """)
        
        # جدول اعضای کلن
        await db.execute("""
            CREATE TABLE IF NOT EXISTS clan_members (
                clan_id INTEGER,
                user_id INTEGER,
                role TEXT DEFAULT 'ژنرال ارشد',
                joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (clan_id, user_id),
                FOREIGN KEY (clan_id) REFERENCES clans(id),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        """)
        
        # جدول تجهیزات
        await db.execute("""
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                equipment_type TEXT,
                name TEXT,
                quantity INTEGER,
                max_uses INTEGER,
                remaining_uses INTEGER,
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        """)
        
        # جدول گیفت
        await db.execute("""
            CREATE TABLE IF NOT EXISTS gifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER,
                receiver_id INTEGER,
                amount INTEGER,
                equipment_type TEXT,
                equipment_count INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول حملات
        await db.execute("""
            CREATE TABLE IF NOT EXISTS attacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attacker_id INTEGER,
                defender_id INTEGER,
                attacker_power INTEGER,
                defender_power INTEGER,
                damage_dealt INTEGER,
                loot_amount INTEGER,
                won INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول تنظیمات
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # جدول پیام‌های مدیریت
        await db.execute("""
            CREATE TABLE IF NOT EXISTS admin_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_text TEXT,
                sent_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.commit()


# ═══════════════════════════════════════════════════════════
# عملیات بازیکنان
# ═══════════════════════════════════════════════════════════

async def create_player(user_id: int, username: str, first_name: str, 
                        country_name: str, invite_code: str = None,
                        invited_by: int = None) -> bool:
    """ایجاد بازیکن جدید"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        try:
            await db.execute("""
                INSERT INTO players (user_id, username, first_name, country_name, 
                                   invite_code, invited_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, username, first_name, country_name, invite_code, invited_by))
            await db.commit()
            return True
        except:
            return False


async def get_player(user_id: int) -> Optional[Dict[str, Any]]:
    """دریافت اطلاعات بازیکن"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM players WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def update_player_money(user_id: int, amount: int):
    """به‌روزرسانی پول بازیکن"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE players SET money = money + ? WHERE user_id = ?",
            (amount, user_id)
        )
        await db.commit()


async def update_player_treasury(user_id: int, amount: int):
    """به‌روزرسانی خزانه بازیکن"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE players SET treasury = treasury + ? WHERE user_id = ?",
            (amount, user_id)
        )
        await db.commit()


async def update_player_defense(user_id: int, amount: int):
    """به‌روزرسانی قدرت دفاعی"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE players SET defense_power = ? WHERE user_id = ?",
            (max(0, amount), user_id)
        )
        await db.commit()


async def update_player_score(user_id: int, score: int):
    """به‌روزرسانی امتیاز"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE players SET score = score + ?, weekly_score = weekly_score + ? WHERE user_id = ?",
            (score, score, user_id)
        )
        await db.commit()


async def get_all_players_sorted() -> List[Dict[str, Any]]:
    """دریافت همه بازیکنان به ترتیب حروف الفبا (اعداد، انگلیسی، فارسی)"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT user_id, country_name, military_power, defense_power, score FROM players ORDER BY country_name"
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def search_player(country_name: str) -> List[Dict[str, Any]]:
    """جستجوی بازیکن بر اساس نام کشور"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT user_id, country_name, military_power, defense_power FROM players WHERE country_name LIKE ?",
            (f"%{country_name}%",)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


# ═══════════════════════════════════════════════════════════
# عملیات کلن
# ═══════════════════════════════════════════════════════════

async def create_clan(name: str, leader_id: int) -> bool:
    """ایجاد کلن جدید"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        try:
            cursor = await db.execute(
                "INSERT INTO clans (name, leader_id) VALUES (?, ?)",
                (name, leader_id)
            )
            clan_id = cursor.lastrowid
            await db.execute(
                "INSERT INTO clan_members (clan_id, user_id, role) VALUES (?, ?, 'شاه')",
                (clan_id, leader_id)
            )
            await db.commit()
            return True
        except:
            return False


async def get_clan_by_name(name: str) -> Optional[Dict[str, Any]]:
    """دریافت کلن بر اساس نام"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM clans WHERE name = ?", (name,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_clan_by_leader(user_id: int) -> Optional[Dict[str, Any]]:
    """دریافت کلن بر اساس لیدر"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM clans WHERE leader_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_player_clan(user_id: int) -> Optional[Dict[str, Any]]:
    """دریافت کلن بازیکن"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT c.*, cm.role 
            FROM clans c
            JOIN clan_members cm ON c.id = cm.clan_id
            WHERE cm.user_id = ?
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_clan_members(clan_id: int) -> List[Dict[str, Any]]:
    """دریافت اعضای کلن"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT p.user_id, p.country_name, p.military_power, cm.role
            FROM players p
            JOIN clan_members cm ON p.user_id = cm.user_id
            WHERE cm.clan_id = ?
            ORDER BY 
                CASE cm.role
                    WHEN 'شاه' THEN 1
                    WHEN 'نخست وزیر' THEN 2
                    ELSE 3
                END
        """, (clan_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def join_clan(clan_id: int, user_id: int) -> bool:
    """پیوستن به کلن"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        try:
            # بررسی ظرفیت
            cursor = await db.execute(
                "SELECT max_members FROM clans WHERE id = ?", (clan_id,)
            )
            row = await cursor.fetchone()
            if not row:
                return False
            
            current_count = await db.execute(
                "SELECT COUNT(*) FROM clan_members WHERE clan_id = ?", (clan_id,)
            )
            count_row = await current_count.fetchone()
            if count_row[0] >= row[0]:
                return False
            
            await db.execute(
                "INSERT INTO clan_members (clan_id, user_id) VALUES (?, ?)",
                (clan_id, user_id)
            )
            await db.commit()
            return True
        except:
            return False


async def leave_clan(user_id: int):
    """ترک کلن"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "DELETE FROM clan_members WHERE user_id = ?", (user_id,)
        )
        await db.commit()


async def update_clan_member_role(user_id: int, new_role: str):
    """به‌روزرسانی نقش عضو"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE clan_members SET role = ? WHERE user_id = ?",
            (new_role, user_id)
        )
        await db.commit()


async def update_clan_treasury(clan_id: int, amount: int):
    """به‌روزرسانی خزانه کلن"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE clans SET treasury = treasury + ? WHERE id = ?",
            (amount, clan_id)
        )
        await db.commit()


async def upgrade_clan_slots(clan_id: int, new_max: int):
    """ارتقای ظرفیت کلن"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE clans SET max_members = ? WHERE id = ?",
            (new_max, clan_id)
        )
        await db.commit()


async def transfer_clan_leadership(old_leader_id: int, new_leader_id: int):
    """انتقال رهبری کلن"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # دریافت clan_id
        cursor = await db.execute(
            "SELECT id FROM clans WHERE leader_id = ?", (old_leader_id,)
        )
        row = await cursor.fetchone()
        if not row:
            return
        
        clan_id = row[0]
        
        # به‌روزرسانی لیدر کلن
        await db.execute(
            "UPDATE clans SET leader_id = ? WHERE id = ?",
            (new_leader_id, clan_id)
        )
        
        # به‌روزرسانی نقش‌ها
        await db.execute(
            "UPDATE clan_members SET role = 'ژنرال ارشد' WHERE user_id = ? AND clan_id = ?",
            (old_leader_id, clan_id)
        )
        await db.execute(
            "UPDATE clan_members SET role = 'شاه' WHERE user_id = ? AND clan_id = ?",
            (new_leader_id, clan_id)
        )
        
        await db.commit()


async def get_all_clans_sorted() -> List[Dict[str, Any]]:
    """دریافت همه کلن‌ها برای لیدربورد"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT c.id, c.name, c.leader_id, c.treasury,
                   (SELECT SUM(p.military_power) FROM players p 
                    JOIN clan_members cm ON p.user_id = cm.user_id 
                    WHERE cm.clan_id = c.id) as total_power,
                   (SELECT COUNT(*) FROM clan_members WHERE clan_id = c.id) as member_count
            FROM clans c
            ORDER BY total_power DESC
        """) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


# ═══════════════════════════════════════════════════════════
# عملیات تجهیزات
# ═══════════════════════════════════════════════════════════

async def add_equipment(user_id: int, equipment_type: str, name: str, 
                       quantity: int, max_uses: int = None):
    """افزودن تجهیزات به بازیکن"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # بررسی وجود تجهیز مشابه
        cursor = await db.execute("""
            SELECT id, quantity, remaining_uses FROM equipment 
            WHERE user_id = ? AND name = ?
        """, (user_id, name))
        row = await cursor.fetchone()
        
        if row:
            new_remaining = row[2] + (max_uses or 1) * quantity
            await db.execute("""
                UPDATE equipment 
                SET quantity = quantity + ?, remaining_uses = ?
                WHERE id = ?
            """, (quantity, new_remaining, row[0]))
        else:
            remaining = (max_uses or 1) * quantity
            await db.execute("""
                INSERT INTO equipment (user_id, equipment_type, name, quantity, max_uses, remaining_uses)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, equipment_type, name, quantity, max_uses or 1, remaining))
        
        await db.commit()


async def get_player_equipment(user_id: int) -> List[Dict[str, Any]]:
    """دریافت تجهیزات بازیکن"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM equipment WHERE user_id = ?", (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def use_equipment(equipment_id: int, uses: int = 1) -> bool:
    """استفاده از تجهیزات"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT remaining_uses FROM equipment WHERE id = ?", (equipment_id,)
        )
        row = await cursor.fetchone()
        if not row or row[0] < uses:
            return False
        
        new_uses = row[0] - uses
        if new_uses <= 0:
            await db.execute("DELETE FROM equipment WHERE id = ?", (equipment_id,))
        else:
            await db.execute(
                "UPDATE equipment SET remaining_uses = ?, quantity = ? WHERE id = ?",
                (new_uses, (new_uses // (row[0] // uses)) + 1, equipment_id)
            )
        
        await db.commit()
        return True


async def remove_equipment(user_id: int, equipment_name: str, count: int) -> bool:
    """حذف تجهیزات"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT id, remaining_uses, max_uses FROM equipment WHERE user_id = ? AND name = ?",
            (user_id, equipment_name)
        )
        row = await cursor.fetchone()
        if not row:
            return False
        
        uses_to_remove = row[2] * count
        new_uses = row[1] - uses_to_remove
        
        if new_uses <= 0:
            await db.execute(
                "DELETE FROM equipment WHERE id = ?", (row[0],)
            )
        else:
            await db.execute(
                "UPDATE equipment SET remaining_uses = ?, quantity = ? WHERE id = ?",
                (new_uses, (new_uses // row[2]), row[0])
            )
        
        await db.commit()
        return True


# ═══════════════════════════════════════════════════════════
# عملیات حمله
# ═══════════════════════════════════════════════════════════

async def record_attack(attacker_id: int, defender_id: int, 
                       attacker_power: int, defender_power: int,
                       damage_dealt: int, loot: int, won: bool):
    """ثبت حمله"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO attacks (attacker_id, defender_id, attacker_power, 
                               defender_power, damage_dealt, loot_amount, won)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (attacker_id, defender_id, attacker_power, defender_power, 
              damage_dealt, loot, 1 if won else 0))
        await db.commit()


# ═══════════════════════════════════════════════════════════
# عملیات تنظیمات
# ═══════════════════════════════════════════════════════════

async def get_setting(key: str) -> Optional[str]:
    """دریافت تنظیم"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None


async def set_setting(key: str, value: str):
    """تنظیم مقدار"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
        """, (key, value))
        await db.commit()


async def is_war_active() -> bool:
    """بررسی فعال بودن جنگ"""
    status = await get_setting("war_active")
    return status == "true"


# ═══════════════════════════════════════════════════════════
# عملیات گیفت
# ═══════════════════════════════════════════════════════════

async def send_gift(sender_id: int, receiver_id: int, amount: int = 0,
                   equipment_type: str = None, equipment_count: int = 0):
    """ارسال هدیه"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO gifts (sender_id, receiver_id, amount, equipment_type, equipment_count)
            VALUES (?, ?, ?, ?, ?)
        """, (sender_id, receiver_id, amount, equipment_type, equipment_count))
        await db.commit()


# ═══════════════════════════════════════════════════════════
# عملیات کمک نظامی
# ═══════════════════════════════════════════════════════════

async def can_send_military_aid(user_id: int) -> bool:
    """بررسی امکان ارسال کمک نظامی"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT last_military_aid, military_aid_count FROM players WHERE user_id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
        if not row:
            return False
        
        last_aid = row[0]
        count = row[1]
        
        if last_aid:
            last_date = datetime.fromisoformat(last_aid)
            if datetime.now().date() > last_date.date():
                return True
        
        return count < 10


async def record_military_aid(user_id: int):
    """ثبت کمک نظامی"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        today = datetime.now().date().isoformat()
        
        cursor = await db.execute(
            "SELECT last_military_aid FROM players WHERE user_id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
        
        if row and row[0]:
            last_date = datetime.fromisoformat(row[0]).date()
            if datetime.now().date() > last_date:
                await db.execute(
                    "UPDATE players SET last_military_aid = ?, military_aid_count = 1 WHERE user_id = ?",
                    (today, user_id)
                )
            else:
                await db.execute(
                    "UPDATE players SET military_aid_count = military_aid_count + 1 WHERE user_id = ?",
                    (user_id,)
                )
        else:
            await db.execute(
                "UPDATE players SET last_military_aid = ?, military_aid_count = 1 WHERE user_id = ?",
                (today, user_id)
            )
        
        await db.commit()


# ═══════════════════════════════════════════════════════════
# لیدربورد
# ═══════════════════════════════════════════════════════════

async def get_leaderboard(limit: int = 100) -> List[Dict[str, Any]]:
    """دریافت لیدربورد"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT user_id, country_name, score, weekly_score, military_power
            FROM players
            ORDER BY weekly_score DESC
            LIMIT ?
        """, (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def reset_weekly_scores():
    """ریست امتیازات هفتگی"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE players SET weekly_score = 0")
        await db.commit()


# ═══════════════════════════════════════════════════════════
# آمار
# ═══════════════════════════════════════════════════════════

async def get_total_players() -> int:
    """تعداد کل بازیکنان"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM players")
        row = await cursor.fetchone()
        return row[0] if row else 0


async def get_total_clans() -> int:
    """تعداد کل کلن‌ها"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM clans")
        row = await cursor.fetchone()
        return row[0] if row else 0