"""
تجهیزات بازی - شامل تجهیزات اقتصادی، نظامی و دفاعی
"""

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Equipment:
    """ساختار تجهیزات"""
    id: str
    name: str
    name_fa: str
    category: str  # economic, military, defense
    price: int
    effect: int  # سود، قدرت حمله، قدرت دفاع
    description: str
    max_uses: int = 1  # تعداد استفاده (1 = یکبار مصرف)


# ═══════════════════════════════════════════════════════════
# تجهیزات اقتصادی
# ═══════════════════════════════════════════════════════════

ECONOMIC_EQUIPMENT: List[Equipment] = [
    Equipment(
        id="nuclear_plant",
        name="Nuclear Power Plant",
        name_fa="نیروگاه انرژی اتمی",
        category="economic",
        price=1_000_000,
        effect=750_000,
        description="⚡ نیروگاه اتمی: سود ۷۵۰,۰۰۰ در روز",
        max_uses=1
    ),
    Equipment(
        id="commercial_port",
        name="Commercial Port",
        name_fa="بندر تجاری",
        category="economic",
        price=50_000,
        effect=20_000,
        description="🚢 بندر تجاری: سود ۲۰,۰۰۰ در روز",
        max_uses=1
    ),
    Equipment(
        id="refinery",
        name="Oil Refinery",
        name_fa="پالایشگاه نفت",
        category="economic",
        price=100_000,
        effect=45_000,
        description="🏭 پالایشگاه: سود ۴۵,۰۰۰ در روز",
        max_uses=1
    ),
    Equipment(
        id="gold_mine",
        name="Gold Mine",
        name_fa="معدن طلا",
        category="economic",
        price=200_000,
        effect=90_000,
        description="⛏️ معدن طلا: سود ۹۰,۰۰۰ در روز",
        max_uses=1
    ),
    Equipment(
        id="tech_company",
        name="Technology Company",
        name_fa="شرکت فناوری",
        category="economic",
        price=300_000,
        effect=150_000,
        description="💻 شرکت فناوری: سود ۱۵۰,۰۰۰ در روز",
        max_uses=1
    ),
    Equipment(
        id="bank",
        name="National Bank",
        name_fa="بانک ملی",
        category="economic",
        price=500_000,
        effect=280_000,
        description="🏦 بانک ملی: سود ۲۸۰,۰۰۰ در روز",
        max_uses=1
    ),
    Equipment(
        id="diamond_mine",
        name="Diamond Mine",
        name_fa="معدن الماس",
        category="economic",
        price=800_000,
        effect=500_000,
        description="💎 معدن الماس: سود ۵۰۰,۰۰۰ در روز",
        max_uses=1
    ),
    Equipment(
        id="space_station",
        name="Space Station",
        name_fa="ایستگاه فضایی",
        category="economic",
        price=2_000_000,
        effect=1_500_000,
        description="🚀 ایستگاه فضایی: سود ۱,۵۰۰,۰۰۰ در روز",
        max_uses=1
    ),
]


# ═══════════════════════════════════════════════════════════
# تجهیزات نظامی (جنگنده - قابل استفاده چندباره)
# ═══════════════════════════════════════════════════════════

MILITARY_EQUIPMENT: List[Equipment] = [
    Equipment(
        id="tank",
        name="Battle Tank",
        name_fa="تانک جنگی",
        category="military",
        price=80_000,
        effect=500,
        description="🔴 تانک: قدرت ۵۰۰ | قابل استفاده تا ۱۰ مرتبه",
        max_uses=10
    ),
    Equipment(
        id="artillery",
        name="Artillery",
        name_fa="توپخانه",
        category="military",
        price=120_000,
        effect=800,
        description="🔴 توپخانه: قدرت ۸۰۰ | قابل استفاده تا ۱۰ مرتبه",
        max_uses=10
    ),
    Equipment(
        id="fighter_jet",
        name="Fighter Jet",
        name_fa="جنگنده هوایی",
        category="military",
        price=200_000,
        effect=1500,
        description="🔴 جنگنده: قدرت ۱,۵۰۰ | قابل استفاده تا ۱۰ مرتبه",
        max_uses=10
    ),
    Equipment(
        id="submarine",
        name="Submarine",
        name_fa="زیردریایی",
        category="military",
        price=300_000,
        effect=2500,
        description="🔴 زیردریایی: قدرت ۲,۵۰۰ | قابل استفاده تا ۱۰ مرتبه",
        max_uses=10
    ),
    Equipment(
        id="warship",
        name="Battleship",
        name_fa="کشتی جنگی",
        category="military",
        price=400_000,
        effect=3500,
        description="🔴 کشتی جنگی: قدرت ۳,۵۰۰ | قابل استفاده تا ۱۰ مرتبه",
        max_uses=10
    ),
    Equipment(
        id="helicopter",
        name="Attack Helicopter",
        name_fa="هلیکوپتر جنگی",
        category="military",
        price=250_000,
        effect=2000,
        description="🔴 هلیکوپتر: قدرت ۲,۰۰۰ | قابل استفاده تا ۱۰ مرتبه",
        max_uses=10
    ),
    Equipment(
        id="missile",
        name="Cruise Missile",
        name_fa="موشک کروز",
        category="military",
        price=350_000,
        effect=3000,
        description="🔴 موشک کروز: قدرت ۳,۰۰۰ | قابل استفاده تا ۱۰ مرتبه",
        max_uses=10
    ),
    Equipment(
        id="bomber",
        name="Strategic Bomber",
        name_fa="بمب‌افکن استراتژیک",
        category="military",
        price=500_000,
        effect=5000,
        description="🔴 بمب‌افکن: قدرت ۵,۰۰۰ | قابل استفاده تا ۱۰ مرتبه",
        max_uses=10
    ),
    Equipment(
        id="drone",
        name="Attack Drone",
        name_fa="پهپاد تهاجمی",
        category="military",
        price=150_000,
        effect=1200,
        description="🔴 پهپاد: قدرت ۱,۲۰۰ | قابل استفاده تا ۱۰ مرتبه",
        max_uses=10
    ),
    Equipment(
        id="nuclear_missile",
        name="Nuclear Missile",
        name_fa="موشک اتمی",
        category="military",
        price=2_000_000,
        effect=15000,
        description="☢️ موشک اتمی: قدرت ۱۵,۰۰۰ | قابل استفاده تا ۱۰ مرتبه | ضریب ۳x",
        max_uses=10
    ),
]


# ═══════════════════════════════════════════════════════════
# تجهیزات دفاعی
# ═══════════════════════════════════════════════════════════

DEFENSE_EQUIPMENT: List[Equipment] = [
    Equipment(
        id="wall",
        name="Fortress Wall",
        name_fa="دیوار قلعه",
        category="defense",
        price=50_000,
        effect=300,
        description="🛡️ دیوار قلعه: دفاع ۳۰۰",
        max_uses=1
    ),
    Equipment(
        id="bunker",
        name="Bunker",
        name_fa="پناهگاه",
        category="defense",
        price=100_000,
        effect=700,
        description="🛡️ پناهگاه: دفاع ۷۰۰",
        max_uses=1
    ),
    Equipment(
        id="sam_system",
        name="SAM System",
        name_fa="سامانه ضد موشک",
        category="defense",
        price=200_000,
        effect=1500,
        description="🛡️ ضد موشک: دفاع ۱,۵۰۰",
        max_uses=1
    ),
    Equipment(
        id="radar",
        name="Radar System",
        name_fa="رادار نظامی",
        category="defense",
        price=150_000,
        effect=1000,
        description="🛡️ رادار: دفاع ۱,۰۰۰",
        max_uses=1
    ),
    Equipment(
        id="shield_generator",
        name="Shield Generator",
        name_fa="ژنراتور سپر",
        category="defense",
        price=300_000,
        effect=2500,
        description="🛡️ ژنراتور سپر: دفاع ۲,۵۰۰",
        max_uses=1
    ),
    Equipment(
        id="laser_defense",
        name="Laser Defense",
        name_fa="سامانه لیزری",
        category="defense",
        price=400_000,
        effect=3500,
        description="🛡️ لیزر: دفاع ۳,۵۰۰",
        max_uses=1
    ),
    Equipment(
        id="nuclear_shelter",
        name="Nuclear Shelter",
        name_fa="پناهگاه اتمی",
        category="defense",
        price=500_000,
        effect=5000,
        description="🛡️ پناهگاه اتمی: دفاع ۵,۰۰۰",
        max_uses=1
    ),
    Equipment(
        id="iron_dome",
        name="Iron Dome",
        name_fa="گنبد آهنین",
        category="defense",
        price=800_000,
        effect=8000,
        description="🛡️ گنبد آهنین: دفاع ۸,۰۰۰",
        max_uses=1
    ),
]


# ═══════════════════════════════════════════════════════════
# همه تجهیزات
# ═══════════════════════════════════════════════════════════

ALL_EQUIPMENT: Dict[str, Equipment] = {}

for eq in ECONOMIC_EQUIPMENT:
    ALL_EQUIPMENT[eq.id] = eq

for eq in MILITARY_EQUIPMENT:
    ALL_EQUIPMENT[eq.id] = eq

for eq in DEFENSE_EQUIPMENT:
    ALL_EQUIPMENT[eq.id] = eq


def get_equipment_by_id(equipment_id: str) -> Equipment:
    """دریافت تجهیزات با آیدی"""
    return ALL_EQUIPMENT.get(equipment_id)


def get_equipment_by_name(name: str) -> Equipment:
    """دریافت تجهیزات با نام"""
    for eq in ALL_EQUIPMENT.values():
        if eq.name.lower() == name.lower() or eq.name_fa == name:
            return eq
    return None


def calculate_profit(price: int) -> int:
    """
    محاسبه سود بر اساس قیمت
    فرمول: هرچه بیشتر پول بدی، سود بیشتری میگیری
    """
    if price <= 0:
        return 0
    
    # فرمول: سود = قیمت * 0.4 + (قیمت / 1000) * 10
    profit = int(price * 0.4 + (price / 1000) * 10)
    return profit


def format_equipment_list(equipment_list: List[Equipment], 
                           show_price: bool = True) -> str:
    """فرمت لیست تجهیزات برای نمایش"""
    result = []
    for eq in equipment_list:
        line = f"▫️ {eq.name_fa}\n"
        line += f"   {eq.description}"
        if show_price:
            line += f"\n   💰 قیمت: {eq.price:,} سکه"
        result.append(line)
    return "\n\n".join(result)


def get_category_name_fa(category: str) -> str:
    """نام فارسی دسته‌بندی"""
    names = {
        "economic": "💰 اقتصادی",
        "military": "⚔️ نظامی",
        "defense": "🛡️ دفاعی"
    }
    return names.get(category, category)