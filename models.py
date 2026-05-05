"""
مدل‌های داده برای بازی
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class ClanRole(Enum):
    """نقش‌های کلن"""
    KING = "شاه"           # سازنده کلن
    PRIME_MINISTER = "نخست وزیر"  # فقط یک نفر
    GENERAL = "ژنرال ارشد"  # نامحدود


class EquipmentCategory(Enum):
    """دسته‌بندی تجهیزات"""
    ECONOMIC = "economic"
    MILITARY = "military"
    DEFENSE = "defense"


@dataclass
class Player:
    """بازیکن"""
    user_id: int
    username: str = ""
    first_name: str = ""
    country_name: str = ""
    money: int = 2_000_000
    treasury: int = 0
    military_power: int = 0
    defense_power: int = 100
    score: int = 0
    weekly_score: int = 0
    invite_code: str = ""
    invited_by: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    # کمک نظامی
    last_military_aid: Optional[str] = None
    military_aid_count: int = 0
    
    # کلن
    clan_id: Optional[int] = None
    clan_role: Optional[str] = None


@dataclass
class Clan:
    """کلن"""
    id: int
    name: str
    leader_id: int
    treasury: int = 0
    max_members: int = 5
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Equipment:
    """تجهیزات"""
    id: int
    user_id: int
    equipment_type: str
    name: str
    quantity: int
    max_uses: int = 1
    remaining_uses: int = 1


@dataclass
class Attack:
    """حمله"""
    id: int
    attacker_id: int
    defender_id: int
    attacker_power: int
    defender_power: int
    damage_dealt: int
    loot_amount: int
    won: bool
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Gift:
    """گیفت"""
    id: int
    sender_id: int
    receiver_id: int
    amount: int = 0
    equipment_type: Optional[str] = None
    equipment_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)