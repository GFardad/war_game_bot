"""
کیبوردهای شیشه‌ای (Inline Keyboard) برای ربات
"""

from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# ═══════════════════════════════════════════════════════════
# کیبوردهای اصلی
# ═══════════════════════════════════════════════════════════

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """منوی اصلی"""
    keyboard = [
        [
            InlineKeyboardButton(text="👤 کشور من", callback_data="my_country"),
            InlineKeyboardButton(text="💰 خزانه", callback_data="treasury"),
        ],
        [
            InlineKeyboardButton(text="⚔️ حمله", callback_data="attack_menu"),
            InlineKeyboardButton(text="🛡️ دفاع", callback_data="defense_menu"),
        ],
        [
            InlineKeyboardButton(text="💰 خرید تجهیزات", callback_data="shop_menu"),
            InlineKeyboardButton(text="📦 تجهیزات من", callback_data="my_equipment"),
        ],
        [
            InlineKeyboardButton(text="👥 کلن", callback_data="clan_menu"),
            InlineKeyboardButton(text="🤝 کمک نظامی", callback_data="military_aid"),
        ],
        [
            InlineKeyboardButton(text="🎁 گیفت", callback_data="gift_menu"),
            InlineKeyboardButton(text="📊 لیدربورد", callback_data="leaderboard"),
        ],
        [
            InlineKeyboardButton(text="👥 دعوت دوستان", callback_data="invite_friends"),
            InlineKeyboardButton(text="📢 پیام مدیریت", callback_data="admin_broadcast"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
    """دکمه بازگشت به منوی اصلی"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="main_menu")]
    ])


def get_country_keyboard() -> InlineKeyboardMarkup:
    """منوی کشور"""
    keyboard = [
        [
            InlineKeyboardButton(text="📊 آمار کشور", callback_data="country_stats"),
        ],
        [
            InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ═══════════════════════════════════════════════════════════
# کیبوردهای فروشگاه
# ═══════════════════════════════════════════════════════════

def get_shop_menu_keyboard() -> InlineKeyboardMarkup:
    """منوی فروشگاه"""
    keyboard = [
        [
            InlineKeyboardButton(text="💰 تجهیزات اقتصادی", callback_data="shop_economic"),
        ],
        [
            InlineKeyboardButton(text="⚔️ تجهیزات نظامی", callback_data="shop_military"),
        ],
        [
            InlineKeyboardButton(text="🛡️ تجهیزات دفاعی", callback_data="shop_defense"),
        ],
        [
            InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_equipment_buy_keyboard(equipment_id: str) -> InlineKeyboardMarkup:
    """دکمه‌های خرید تجهیزات"""
    keyboard = [
        [
            InlineKeyboardButton(text="🛒 خرید ۱ عدد", callback_data=f"buy_1_{equipment_id}"),
            InlineKeyboardButton(text="🛒 خرید ۵ عدد", callback_data=f"buy_5_{equipment_id}"),
        ],
        [
            InlineKeyboardButton(text="🛒 خرید ۱۰ عدد", callback_data=f"buy_10_{equipment_id}"),
            InlineKeyboardButton(text="🛒 خرید ۲۵ عدد", callback_data=f"buy_25_{equipment_id}"),
        ],
        [
            InlineKeyboardButton(text="🔙 بازگشت", callback_data="shop_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ═══════════════════════════════════════════════════════════
# کیبوردهای حمله
# ═══════════════════════════════════════════════════════════

def get_attack_menu_keyboard() -> InlineKeyboardMarkup:
    """منوی حمله"""
    keyboard = [
        [
            InlineKeyboardButton(text="🔍 سرچ کشور", callback_data="attack_search"),
        ],
        [
            InlineKeyboardButton(text="📋 لیست همه کشورها", callback_data="attack_list"),
        ],
        [
            InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_attack_target_keyboard(user_id: int, country_name: str) -> InlineKeyboardMarkup:
    """دکمه حمله به هدف"""
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"⚔️ حمله به {country_name}",
                callback_data=f"attack_{user_id}"
            ),
        ],
        [
            InlineKeyboardButton(text="🔙 بازگشت", callback_data="attack_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_attack_list_keyboard(players: List[dict], page: int = 0) -> InlineKeyboardMarkup:
    """لیست بازیکنان برای حمله با صفحه‌بندی"""
    keyboard = []
    
    per_page = 8
    start = page * per_page
    end = start + per_page
    page_players = players[start:end]
    
    for player in page_players:
        keyboard.append([
            InlineKeyboardButton(
                text=f"⚔️ {player['country_name']} (قدرت: {player['military_power']})",
                callback_data=f"attack_{player['user_id']}"
            )
        ])
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="◀️ قبلی", callback_data=f"attack_page_{page-1}")
        )
    if end < len(players):
        nav_buttons.append(
            InlineKeyboardButton(text="بعدی ▶️", callback_data=f"attack_page_{page+1}")
        )
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton(text="🔍 سرچ", callback_data="attack_search")])
    keyboard.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirm_attack_keyboard(attacker_id: int) -> InlineKeyboardMarkup:
    """تأیید حمله"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ تأیید حمله", callback_data=f"confirm_attack_{attacker_id}"),
        ],
        [
            InlineKeyboardButton(text="❌ انصراف", callback_data="attack_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_select_weapons_keyboard(weapons: List[dict]) -> InlineKeyboardMarkup:
    """انتخاب سلاح برای حمله"""
    keyboard = []
    
    for weapon in weapons:
        keyboard.append([
            InlineKeyboardButton(
                text=f"⚔️ {weapon['name']} (تعداد: {weapon['quantity']})",
                callback_data=f"select_weapon_{weapon['id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(text="🔙 انصراف", callback_data="attack_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ═══════════════════════════════════════════════════════════
# کیبوردهای کلن
# ═══════════════════════════════════════════════════════════

def get_clan_menu_keyboard(role: str = None) -> InlineKeyboardMarkup:
    """منوی کلن"""
    keyboard = [
        [
            InlineKeyboardButton(text="👥 اعضای کلن", callback_data="clan_members"),
        ],
        [
            InlineKeyboardButton(text="💰 خزانه کلن", callback_data="clan_treasury"),
        ],
        [
            InlineKeyboardButton(text="📊 لیدربورد کلن", callback_data="clan_leaderboard"),
        ],
    ]
    
    if role == "شاه":
        keyboard.extend([
            [
                InlineKeyboardButton(text="👑 مدیریت اعضا", callback_data="clan_manage"),
            ],
            [
                InlineKeyboardButton(text="💎 ارتقای ظرفیت", callback_data="clan_upgrade"),
            ],
        ])
    elif role == "نخست وزیر":
        keyboard.extend([
            [
                InlineKeyboardButton(text="💎 ارتقای ظرفیت", callback_data="clan_upgrade"),
            ],
        ])
    
    keyboard.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_clan_list_keyboard(clans: List[dict]) -> InlineKeyboardMarkup:
    """لیست کلن‌ها"""
    keyboard = []
    
    for clan in clans:
        keyboard.append([
            InlineKeyboardButton(
                text=f"👥 {clan['name']} (اعضا: {clan['member_count']}/{clan['max_members']})",
                callback_data=f"view_clan_{clan['id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_join_clan_keyboard(clan_id: int) -> InlineKeyboardMarkup:
    """دکمه عضویت در کلن"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ عضویت در کلن", callback_data=f"join_clan_{clan_id}"),
        ],
        [
            InlineKeyboardButton(text="🔙 بازگشت", callback_data="clan_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_clan_member_keyboard(user_id: int, role: str, is_leader: bool = False) -> InlineKeyboardMarkup:
    """دکمه‌های مدیریت عضو کلن"""
    keyboard = []
    
    if is_leader:
        if role == "ژنرال ارشد":
            keyboard.append([
                InlineKeyboardButton(
                    text="📜 ارتقا به نخست وزیر",
                    callback_data=f"promote_pm_{user_id}"
                )
            ])
        elif role == "نخست وزیر":
            keyboard.append([
                InlineKeyboardButton(
                    text="📜 تنزل به ژنرال ارشد",
                    callback_data=f"demote_general_{user_id}"
                )
            ])
        
        if role != "شاه":
            keyboard.append([
                InlineKeyboardButton(
                    text="👑 انتقال رهبری",
                    callback_data=f"transfer_leader_{user_id}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton(
                text="🚪 اخراج از کلن",
                callback_data=f"kick_member_{user_id}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="clan_members")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ═══════════════════════════════════════════════════════════
# کیبوردهای کمک نظامی
# ═══════════════════════════════════════════════════════════

def get_military_aid_menu_keyboard() -> InlineKeyboardMarkup:
    """منوی کمک نظامی"""
    keyboard = [
        [
            InlineKeyboardButton(text="💰 ارسال پول", callback_data="aid_send_money"),
        ],
        [
            InlineKeyboardButton(text="⚔️ ارسال تجهیزات", callback_data="aid_send_equipment"),
        ],
        [
            InlineKeyboardButton(text="🔍 جستجوی بازیکن", callback_data="aid_search"),
        ],
        [
            InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_aid_equipment_keyboard(equipment: List[dict]) -> InlineKeyboardMarkup:
    """انتخاب تجهیزات برای ارسال"""
    keyboard = []
    
    for eq in equipment:
        keyboard.append([
            InlineKeyboardButton(
                text=f"⚔️ {eq['name']} (تعداد: {eq['quantity']})",
                callback_data=f"aid_eq_{eq['id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="military_aid")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ═══════════════════════════════════════════════════════════
# کیبوردهای گیفت
# ═══════════════════════════════════════════════════════════

def get_gift_menu_keyboard() -> InlineKeyboardMarkup:
    """منوی گیفت"""
    keyboard = [
        [
            InlineKeyboardButton(text="💰 ارسال پول", callback_data="gift_send_money"),
        ],
        [
            InlineKeyboardButton(text="🔍 جستجوی بازیکن", callback_data="gift_search"),
        ],
        [
            InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ═══════════════════════════════════════════════════════════
# کیبوردهای لیدربورد
# ═══════════════════════════════════════════════════════════

def get_leaderboard_keyboard() -> InlineKeyboardMarkup:
    """منوی لیدربورد"""
    keyboard = [
        [
            InlineKeyboardButton(text="🏆 لیدربورد بازیکنان", callback_data="lb_players"),
        ],
        [
            InlineKeyboardButton(text="👥 لیدربورد کلن‌ها", callback_data="lb_clans"),
        ],
        [
            InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ═══════════════════════════════════════════════════════════
# کیبوردهای ادمین
# ═══════════════════════════════════════════════════════════

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """منوی ادمین"""
    keyboard = [
        [
            InlineKeyboardButton(text="📢 ارسال پیام همگانی", callback_data="admin_send_broadcast"),
        ],
        [
            InlineKeyboardButton(text="⚔️ فعال/غیرفعال کردن جنگ", callback_data="admin_toggle_war"),
        ],
        [
            InlineKeyboardButton(text="🎁 ارسال گیفت", callback_data="admin_send_gift"),
        ],
        [
            InlineKeyboardButton(text="📊 آمار بازی", callback_data="admin_stats"),
        ],
        [
            InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirm_broadcast_keyboard() -> InlineKeyboardMarkup:
    """تأیید ارسال پیام همگانی"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ ارسال برای همه", callback_data="confirm_broadcast"),
        ],
        [
            InlineKeyboardButton(text="❌ انصراف", callback_data="admin_broadcast"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirm_gift_keyboard(receiver_id: int) -> InlineKeyboardMarkup:
    """تأیید ارسال گیفت ادمین"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ ارسال گیفت", callback_data=f"admin_confirm_gift_{receiver_id}"),
        ],
        [
            InlineKeyboardButton(text="❌ انصراف", callback_data="admin_send_gift"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ═══════════════════════════════════════════════════════════
# کیبوردهای دعوت
# ═══════════════════════════════════════════════════════════

def get_invite_keyboard(invite_link: str) -> InlineKeyboardMarkup:
    """دکمه دعوت"""
    keyboard = [
        [
            InlineKeyboardButton(text="👥 دعوت دوستان", url=invite_link),
        ],
        [
            InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ═══════════════════════════════════════════════════════════
# کیبوردهای تجهیزات من
# ═══════════════════════════════════════════════════════════

def get_my_equipment_keyboard() -> InlineKeyboardMarkup:
    """منوی تجهیزات من"""
    keyboard = [
        [
            InlineKeyboardButton(text="💰 اقتصادی", callback_data="my_eq_economic"),
        ],
        [
            InlineKeyboardButton(text="⚔️ نظامی", callback_data="my_eq_military"),
        ],
        [
            InlineKeyboardButton(text="🛡️ دفاعی", callback_data="my_eq_defense"),
        ],
        [
            InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ═══════════════════════════════════════════════════════════
# کیبوردهای دفاع
# ═══════════════════════════════════════════════════════════

def get_defense_menu_keyboard() -> InlineKeyboardMarkup:
    """منوی دفاع"""
    keyboard = [
        [
            InlineKeyboardButton(text="📊 وضعیت دفاع", callback_data="defense_status"),
        ],
        [
            InlineKeyboardButton(text="🛡️ خرید تجهیزات دفاعی", callback_data="shop_defense"),
        ],
        [
            InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ═══════════════════════════════════════════════════════════
# کیبوردهای خزانه
# ═══════════════════════════════════════════════════════════

def get_treasury_keyboard() -> InlineKeyboardMarkup:
    """منوی خزانه"""
    keyboard = [
        [
            InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ═══════════════════════════════════════════════════════════
# کیبوردهای سرچ
# ═══════════════════════════════════════════════════════════

def get_search_result_keyboard(results: List[dict], action: str) -> InlineKeyboardMarkup:
    """نتایج جستجو"""
    keyboard = []
    
    for result in results[:10]:
        if action == "attack":
            keyboard.append([
                InlineKeyboardButton(
                    text=f"⚔️ {result['country_name']}",
                    callback_data=f"attack_{result['user_id']}"
                )
            ])
        elif action == "aid":
            keyboard.append([
                InlineKeyboardButton(
                    text=f"⚔️ {result['country_name']}",
                    callback_data=f"aid_to_{result['user_id']}"
                )
            ])
        elif action == "gift":
            keyboard.append([
                InlineKeyboardButton(
                    text=f"🎁 {result['country_name']}",
                    callback_data=f"gift_to_{result['user_id']}"
                )
            ])
    
    keyboard.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)