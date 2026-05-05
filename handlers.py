"""
هندلرهای اصلی ربات - پاسخ به کلیک‌ها و دستورات
"""

import re
import uuid
from datetime import datetime
from typing import Optional

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.filters.text import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import aiosqlite

import config
import database as db
from keyboards import *
from equipment import (
    ECONOMIC_EQUIPMENT, MILITARY_EQUIPMENT, DEFENSE_EQUIPMENT,
    ALL_EQUIPMENT, get_category_name_fa, format_equipment_list
)
from scheduler import calculate_player_hourly_profit


# ═══════════════════════════════════════════════════════════
# ماشین حالت (FSM)
# ═══════════════════════════════════════════════════════════

class GameStates(StatesGroup):
    """حالات مختلف بازی"""
    waiting_for_country_name = State()
    waiting_for_clan_name = State()
    waiting_for_attack_target = State()
    waiting_for_aid_money = State()
    waiting_for_aid_target = State()
    waiting_for_gift_money = State()
    waiting_for_gift_target = State()
    waiting_for_search = State()
    waiting_for_broadcast = State()
    waiting_for_admin_gift = State()


# ═══════════════════════════════════════════════════════════
# بررسی‌های اولیه
# ═══════════════════════════════════════════════════════════

def is_admin(user_id: int) -> bool:
    """بررسی ادمین بودن"""
    return user_id in config.ADMIN_IDS


async def check_player_exists(user_id: int) -> bool:
    """بررسی وجود بازیکن"""
    player = await db.get_player(user_id)
    return player is not None


# ═══════════════════════════════════════════════════════════
# دستور /start
# ═══════════════════════════════════════════════════════════

async def cmd_start(message: types.Message, state: FSMContext):
    """شروع ربات"""
    user_id = message.from_user.id
    
    # بررسی کد دعوت
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    invite_code = args[0] if args else None
    
    # بررسی وجود بازیکن
    player = await db.get_player(user_id)
    
    if not player:
        # ایجاد کد دعوت
        new_invite_code = str(uuid.uuid4())[:8]
        
        await db.create_player(
            user_id=user_id,
            username=message.from_user.username or "",
            first_name=message.from_user.first_name or "",
            country_name="",
            invite_code=new_invite_code,
            invited_by=None
        )
        
        # پاداش دعوت‌کننده
        if invite_code:
            inviter = await db.get_player_by_invite_code(invite_code)
            if inviter:
                await db.update_player_money(inviter['user_id'], 500_000)
                await db.update_player_money(user_id, 500_000)
                await db.send_gift(inviter['user_id'], user_id, 500_000)
        
        # درخواست نام کشور
        await message.answer(
            "🌍 به ربات جنگ جهانی خوش آمدید!\n\n"
            "💰 شما ۲,۰۰۰,۰۰۰ سکه دریافت کردید.\n\n"
            "🏳️ لطفاً نام کشور خود را وارد کنید:",
            reply_markup=get_back_to_main_keyboard()
        )
        await state.set_state(GameStates.waiting_for_country_name)
    else:
        if not player['country_name']:
            await message.answer(
                "🏳️ لطفاً نام کشور خود را وارد کنید:",
                reply_markup=get_back_to_main_keyboard()
            )
            await state.set_state(GameStates.waiting_for_country_name)
        else:
            await show_main_menu(message)


# ═══════════════════════════════════════════════════════════
# ثبت نام کشور
# ═══════════════════════════════════════════════════════════

async def process_country_name(message: types.Message, state: FSMContext):
    """ثبت نام کشور"""
    user_id = message.from_user.id
    country_name = message.text.strip()
    
    if len(country_name) < 2:
        await message.answer("❌ نام کشور باید حداقل ۲ کاراکتر باشد.")
        return
    
    if len(country_name) > 30:
        await message.answer("❌ نام کشور نباید بیشتر از ۳۰ کاراکتر باشد.")
        return
    
    # به‌روزرسانی نام کشور
    async with aiosqlite.connect(db.DATABASE_PATH) as db_conn:
        await db_conn.execute(
            "UPDATE players SET country_name = ? WHERE user_id = ?",
            (country_name, user_id)
        )
        await db_conn.commit()
    
    await state.clear()
    
    await message.answer(
        f"✅ کشور '{country_name}' با موفقیت ثبت شد!\n\n"
        f"💰 موجودی: ۲,۰۰۰,۰۰۰ سکه\n\n"
        f"حالا می‌توانید بازی کنید!",
        reply_markup=get_main_menu_keyboard()
    )


# ═══════════════════════════════════════════════════════════
# منوی اصلی
# ═══════════════════════════════════════════════════════════

async def show_main_menu(message_or_callback, is_callback=False):
    """نمایش منوی اصلی"""
    if is_callback:
        user_id = message_or_callback.from_user.id
        edit_func = message_or_callback.message.edit_text
    else:
        user_id = message_or_callback.from_user.id
        edit_func = None
    
    player = await db.get_player(user_id)
    
    if not player or not player['country_name']:
        await message_or_callback.answer(
            "🏳️ لطفاً ابتدا نام کشور خود را ثبت کنید.\n/start را بزنید.",
            reply_markup=get_back_to_main_keyboard()
        )
        return
    
    # محاسبه سود ساعتی
    hourly_profit = await calculate_player_hourly_profit(user_id)
    
    text = (
        f"🎮 منوی اصلی\n\n"
        f"👤 کشور: {player['country_name']}\n"
        f"💰 خزانه: {player['money']:,} سکه\n"
        f"⚔️ قدرت نظامی: {player['military_power']}\n"
        f"🛡️ قدرت دفاعی: {player['defense_power']}\n"
        f"💵 سود ساعتی: {hourly_profit:,} سکه"
    )
    
    if edit_func:
        await edit_func(text, reply_markup=get_main_menu_keyboard())
    else:
        await message_or_callback.answer(text, reply_markup=get_main_menu_keyboard())


async def cmd_main_menu(callback: types.CallbackQuery, state: FSMContext):
    """دکمه منوی اصلی"""
    await state.clear()
    await show_main_menu(callback, is_callback=True)


# ═══════════════════════════════════════════════════════════
# مدیریت کشور
# ═══════════════════════════════════════════════════════════

async def show_country(callback: types.CallbackQuery):
    """نمایش اطلاعات کشور"""
    player = await db.get_player(callback.from_user.id)
    
    if not player:
        return
    
    hourly_profit = await calculate_player_hourly_profit(callback.from_user.id)
    
    text = (
        f"👤 کشور: {player['country_name']}\n\n"
        f"💰 خزانه: {player['money']:,} سکه\n"
        f"⚔️ قدرت نظامی: {player['military_power']}\n"
        f"🛡️ قدرت دفاعی: {player['defense_power']}\n"
        f"🏆 امتیاز: {player['score']}\n"
        f"💵 سود هر ساعت: {hourly_profit:,} سکه"
    )
    
    await callback.message.edit_text(text, reply_markup=get_country_keyboard())


async def show_country_stats(callback: types.CallbackQuery):
    """نمایش آمار کشور"""
    player = await db.get_player(callback.from_user.id)
    equipment = await db.get_player_equipment(callback.from_user.id)
    
    if not player:
        return
    
    economic = [e for e in equipment if e['equipment_type'] == 'economic']
    military = [e for e in equipment if e['equipment_type'] == 'military']
    defense = [e for e in equipment if e['equipment_type'] == 'defense']
    
    text = (
        f"📊 آمار کشور {player['country_name']}\n\n"
        f"💰 خزانه: {player['money']:,} سکه\n"
        f"⚔️ قدرت نظامی: {player['military_power']}\n"
        f"🛡️ قدرت دفاعی: {player['defense_power']}\n\n"
        f"📦 تجهیزات:\n"
        f"   💰 اقتصادی: {len(economic)} عدد\n"
        f"   ⚔️ نظامی: {len(military)} عدد\n"
        f"   🛡️ دفاعی: {len(defense)} عدد"
    )
    
    await callback.message.edit_text(text, reply_markup=get_country_keyboard())


# ═══════════════════════════════════════════════════════════
# فروشگاه
# ═══════════════════════════════════════════════════════════

async def show_shop_menu(callback: types.CallbackQuery):
    """نمایش منوی فروشگاه"""
    text = "🏪 فروشگاه تجهیزات\n\nیک دسته‌بندی را انتخاب کنید:"
    await callback.message.edit_text(text, reply_markup=get_shop_menu_keyboard())


async def show_economic_shop(callback: types.CallbackQuery):
    """نمایش تجهیزات اقتصادی"""
    text = "💰 تجهیزات اقتصادی\n\nاین تجهیزات هر ساعت سود تولید می‌کنند:\n\n"
    text += format_equipment_list(ECONOMIC_EQUIPMENT)
    
    await callback.message.edit_text(text, reply_markup=get_shop_menu_keyboard())


async def show_military_shop(callback: types.CallbackQuery):
    """نمایش تجهیزات نظامی"""
    player = await db.get_player(callback.from_user.id)
    
    text = "⚔️ تجهیزات نظامی\n\n"
    text += "این تجهیزات برای حمله استفاده می‌شوند (تا ۱۰ مرتبه).\n\n"
    text += format_equipment_list(MILITARY_EQUIPMENT)
    text += f"\n\n💰 موجودی شما: {player['money']:,} سکه"
    
    await callback.message.edit_text(text, reply_markup=get_shop_menu_keyboard())


async def show_defense_shop(callback: types.CallbackQuery):
    """نمایش تجهیزات دفاعی"""
    player = await db.get_player(callback.from_user.id)
    
    text = "🛡️ تجهیزات دفاعی\n\n"
    text += "این تجهیزات قدرت دفاعی شما را افزایش می‌دهند.\n\n"
    text += format_equipment_list(DEFENSE_EQUIPMENT)
    text += f"\n\n💰 موجودی شما: {player['money']:,} سکه"
    text += f"\n\n🛡️ قدرت دفاعی فعلی: {player['defense_power']}"
    
    await callback.message.edit_text(text, reply_markup=get_shop_menu_keyboard())


async def process_buy(callback: types.CallbackQuery, state: FSMContext):
    """پردازش خرید"""
    data = callback.data
    
    parts = data.split("_")
    if len(parts) < 3:
        return
    
    amount = int(parts[1])
    equipment_id = "_".join(parts[2:])
    
    equipment = ALL_EQUIPMENT.get(equipment_id)
    if not equipment:
        await callback.answer("❌ تجهیزات یافت نشد!")
        return
    
    player = await db.get_player(callback.from_user.id)
    total_price = equipment.price * amount
    
    if player['money'] < total_price:
        await callback.answer("❌ موجودی کافی نیست!")
        return
    
    # کسر پول
    await db.update_player_money(callback.from_user.id, -total_price)
    
    # افزودن تجهیزات
    await db.add_equipment(
        user_id=callback.from_user.id,
        equipment_type=equipment.category,
        name=equipment_id,
        quantity=amount,
        max_uses=equipment.max_uses
    )
    
    # به‌روزرسانی قدرت
    if equipment.category == 'military':
        new_power = player['military_power'] + (equipment.effect * amount)
        async with aiosqlite.connect(db.DATABASE_PATH) as db_conn:
            await db_conn.execute(
                "UPDATE players SET military_power = ? WHERE user_id = ?",
                (new_power, callback.from_user.id)
            )
            await db_conn.commit()
    
    elif equipment.category == 'defense':
        new_defense = player['defense_power'] + (equipment.effect * amount)
        async with aiosqlite.connect(db.DATABASE_PATH) as db_conn:
            await db_conn.execute(
                "UPDATE players SET defense_power = ? WHERE user_id = ?",
                (new_defense, callback.from_user.id)
            )
            await db_conn.commit()
    
    await callback.answer(f"✅ {amount} عدد {equipment.name_fa} خریداری شد!")


# ═══════════════════════════════════════════════════════════
# حمله
# ═══════════════════════════════════════════════════════════

async def show_attack_menu(callback: types.CallbackQuery):
    """نمایش منوی حمله"""
    war_active = await db.is_war_active()
    
    if not war_active:
        await callback.message.edit_text(
            "⚠️ حمله فعلاً غیرفعال است.\n\n"
            "منتظر بمانید تا ادمین جنگ را فعال کند.",
            reply_markup=get_back_to_main_keyboard()
        )
        return
    
    text = "⚔️ منوی حمله\n\nیک گزینه را انتخاب کنید:"
    await callback.message.edit_text(text, reply_markup=get_attack_menu_keyboard())


async def show_attack_list(callback: types.CallbackQuery):
    """نمایش لیست بازیکنان برای حمله"""
    players = await db.get_all_players_sorted()
    players = [p for p in players if p['user_id'] != callback.from_user.id]
    
    if not players:
        await callback.message.edit_text(
            "❌ بازیکنی برای حمله یافت نشد!",
            reply_markup=get_back_to_main_keyboard()
        )
        return
    
    text = f"⚔️ لیست کشورها ({len(players)} کشور)\n\nیک هدف را انتخاب کنید:"
    await callback.message.edit_text(text, reply_markup=get_attack_list_keyboard(players, 0))


async def show_attack_search(callback: types.CallbackQuery, state: FSMContext):
    """جستجوی بازیکن برای حمله"""
    await callback.message.edit_text(
        "🔍 نام کشور مورد نظر را جستجو کنید:",
        reply_markup=get_back_to_main_keyboard()
    )
    await state.set_state(GameStates.waiting_for_attack_target)


async def process_attack_search(message: types.Message, state: FSMContext):
    """پردازش جستجوی حمله"""
    search = message.text.strip()
    
    results = await db.search_player(search)
    results = [r for r in results if r['user_id'] != message.from_user.id]
    
    if not results:
        await message.answer(
            "❌ کشوری یافت نشد!",
            reply_markup=get_back_to_main_keyboard()
        )
        await state.clear()
        return
    
    text = f"🔍 نتایج جستجو ({len(results)} کشور):\n\nیک هدف را انتخاب کنید:"
    await message.answer(text, reply_markup=get_search_result_keyboard(results, "attack"))
    await state.clear()


async def show_attack_target(callback: types.CallbackQuery, state: FSMContext):
    """نمایش هدف حمله"""
    data = callback.data
    parts = data.split("_")
    if len(parts) < 2:
        return
    
    target_id = int(parts[1])
    target = await db.get_player(target_id)
    
    if not target:
        await callback.answer("❌ بازیکن یافت نشد!")
        return
    
    # بررسی کلن
    attacker_clan = await db.get_player_clan(callback.from_user.id)
    target_clan = await db.get_player_clan(target_id)
    
    if attacker_clan and target_clan and attacker_clan['id'] == target_clan['id']:
        await callback.answer("❌ نمی‌توانید به اعضای کلن خود حمله کنید!")
        return
    
    text = (
        f"⚔️ هدف حمله\n\n"
        f"🏳️ کشور: {target['country_name']}\n"
        f"🛡️ قدرت دفاعی: {target['defense_power']}\n"
        f"💰 خزانه: {target['money']:,} سکه"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_confirm_attack_keyboard(target_id)
    )


async def process_attack(callback: types.CallbackQuery, state: FSMContext):
    """پردازش حمله"""
    data = callback.data
    parts = data.split("_")
    if len(parts) < 3:
        return
    
    target_id = int(parts[2])
    
    attacker = await db.get_player(callback.from_user.id)
    defender = await db.get_player(target_id)
    
    if not attacker or not defender:
        await callback.answer("❌ خطا در اطلاعات!")
        return
    
    # بررسی friendly fire
    attacker_clan = await db.get_player_clan(callback.from_user.id)
    defender_clan = await db.get_player_clan(target_id)
    
    if attacker_clan and defender_clan and attacker_clan['id'] == defender_clan['id']:
        await callback.answer("❌ نمی‌توانید به اعضای کلن خود حمله کنید!")
        return
    
    # محاسبه قدرت حمله
    equipment = await db.get_player_equipment(callback.from_user.id)
    military_equipment = [e for e in equipment if e['equipment_type'] == 'military']
    
    total_attack_power = 0
    used_weapons = []
    
    for eq in military_equipment:
        if eq['remaining_uses'] > 0:
            eq_info = ALL_EQUIPMENT.get(eq['name'])
            if eq_info:
                power = eq_info.effect
                # بررسی سلاح اتمی
                if eq_info.id == 'nuclear_missile':
                    power *= config.ATOMIC_WEAPON_DAMAGE_MULTIPLIER
                total_attack_power += power
                used_weapons.append(eq)
    
    if total_attack_power == 0:
        await callback.answer("❌ تجهیزات نظامی ندارید!")
        return
    
    # محاسبه خسارت
    defense = defender['defense_power']
    damage = max(0, total_attack_power - defense // 2)
    
    # محاسبه غارت
    loot = min(defender['money'], damage // 10)
    
    # نتیجه
    won = total_attack_power > defense
    
    # ثبت حمله
    await db.record_attack(
        attacker_id=callback.from_user.id,
        defender_id=target_id,
        attacker_power=total_attack_power,
        defender_power=defense,
        damage_dealt=damage,
        loot=loot,
        won=won
    )
    
    # کسر تجهیزات نظامی
    for eq in used_weapons:
        await db.use_equipment(eq['id'], 1)
    
    # به‌روزرسانی دفاع هدف
    new_defense = max(0, defense - damage)
    await db.update_player_defense(target_id, new_defense)
    
    # بررسی سقوط کشور
    if new_defense <= 0:
        async with aiosqlite.connect(db.DATABASE_PATH) as db_conn:
            await db_conn.execute(
                "UPDATE players SET country_name = NULL, defense_power = 100, military_power = 0 WHERE user_id = ?",
                (target_id,)
            )
            await db_conn.commit()
        
        try:
            await callback.bot.send_message(
                target_id,
                "💀 کشور شما سقوط کرد!\n\n"
                "برای ادامه بازی، باید یک کشور جدید بسازید.\n"
                "/start را بزنید."
            )
        except:
            pass
    
    # انتقال پول
    if loot > 0:
        await db.update_player_money(callback.from_user.id, loot)
        await db.update_player_money(target_id, -loot)
    
    # به‌روزرسانی امتیاز
    score = damage // 100
    if won:
        score += 1000
    await db.update_player_score(callback.from_user.id, score)
    
    # نتیجه نهایی
    result_text = (
        f"⚔️ نتیجه نبرد\n\n"
        f"🏳️ {attacker['country_name']} vs {defender['country_name']}\n\n"
        f"⚔️ قدرت حمله: {total_attack_power:,}\n"
        f"🛡️ قدرت دفاع: {defense:,}\n\n"
    )
    
    if won:
        result_text += (
            f"✅ پیروزی!\n\n"
            f"💰 غارت: {loot:,} سکه\n"
            f"🛡️ خسارت وارده به دشمن: {damage:,}\n"
            f"🏆 امتیاز: {score:,}"
        )
    else:
        result_text += (
            f"❌ شکست!\n\n"
            f"🛡️ خسارت وارده به دشمن: {damage:,}\n"
            f"🏆 امتیاز: {score:,}"
        )
    
    await callback.message.edit_text(result_text, reply_markup=get_back_to_main_keyboard())


# ═══════════════════════════════════════════════════════════
# کلن
# ═══════════════════════════════════════════════════════════

async def show_clan_menu(callback: types.CallbackQuery):
    """نمایش منوی کلن"""
    player_clan = await db.get_player_clan(callback.from_user.id)
    
    if not player_clan:
        clans = await db.get_all_clans_sorted()
        
        if not clans:
            text = (
                "👥 کلن‌ها\n\n"
                "هنوز کلنی ساخته نشده.\n"
                "می‌توانید یک کلن جدید بسازید."
            )
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="➕ ساخت کلن جدید", callback_data="create_clan")],
                [types.InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu")],
            ])
        else:
            text = "👥 کلن‌های موجود:\n\nیک کلن را انتخاب کنید:"
            keyboard = get_clan_list_keyboard(clans)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
    else:
        text = (
            f"👥 کلن: {player_clan['name']}\n\n"
            f"👑 مقام شما: {player_clan['role']}\n"
            f"👥 اعضا: {len(await db.get_clan_members(player_clan['id']))}/{player_clan['max_members']}\n"
            f"💰 خزانه: {player_clan['treasury']:,} سکه"
        )
        await callback.message.edit_text(text, reply_markup=get_clan_menu_keyboard(player_clan['role']))


async def show_create_clan(callback: types.CallbackQuery, state: FSMContext):
    """ساخت کلن جدید"""
    await callback.message.edit_text(
        "🏰 نام کلن جدید را وارد کنید:",
        reply_markup=get_back_to_main_keyboard()
    )
    await state.set_state(GameStates.waiting_for_clan_name)


async def process_create_clan(message: types.Message, state: FSMContext):
    """پردازش ساخت کلن"""
    name = message.text.strip()
    
    if len(name) < 3:
        await message.answer("❌ نام کلن باید حداقل ۳ کاراکتر باشد.")
        return
    
    existing = await db.get_clan_by_name(name)
    if existing:
        await message.answer("❌ این نام کلن قبلاً استفاده شده است.")
        return
    
    success = await db.create_clan(name, message.from_user.id)
    
    if success:
        await message.answer(
            f"✅ کلن '{name}' با موفقیت ساخته شد!\n\n"
            f"👑 شما رهبر (شاه) این کلن هستید.\n"
            f"👥 ظرفیت: ۵ نفر",
            reply_markup=get_clan_menu_keyboard("شاه")
        )
    else:
        await message.answer("❌ خطا در ساخت کلن!")
    
    await state.clear()


async def show_join_clan(callback: types.CallbackQuery, state: FSMContext):
    """عضویت در کلن"""
    data = callback.data
    parts = data.split("_")
    if len(parts) < 3:
        return
    
    clan_id = int(parts[2])
    
    success = await db.join_clan(clan_id, callback.from_user.id)
    
    if success:
        await callback.answer("✅ به کلن پیوستید!")
        await show_clan_menu(callback)
    else:
        await callback.answer("❌ کلن پر است یا خطایی رخ داده!")


async def show_clan_members(callback: types.CallbackQuery):
    """نمایش اعضای کلن"""
    player_clan = await db.get_player_clan(callback.from_user.id)
    
    if not player_clan:
        await callback.answer("❌ شما عضو کلنی نیستید!")
        return
    
    members = await db.get_clan_members(player_clan['id'])
    
    text = f"👥 اعضای کلن {player_clan['name']}:\n\n"
    
    for i, member in enumerate(members, 1):
        role_emoji = "👑" if member['role'] == 'شاه' else "📜" if member['role'] == 'نخست وزیر' else "⚔️"
        text += f"{i}. {role_emoji} {member['country_name']} - {member['role']}\n"
        text += f"   ⚔️ قدرت: {member['military_power']}\n\n"
    
    is_leader = player_clan['leader_id'] == callback.from_user.id
    
    keyboard = []
    if is_leader:
        for member in members:
            if member['user_id'] != callback.from_user.id:
                keyboard.append([
                    types.InlineKeyboardButton(
                        text=f"⚙️ مدیریت {member['country_name']}",
                        callback_data=f"manage_member_{member['user_id']}"
                    )
                ])
    
    keyboard.append([types.InlineKeyboardButton(text="🔙 بازگشت", callback_data="clan_menu")])
    
    await callback.message.edit_text(
        text,
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


async def show_clan_treasury(callback: types.CallbackQuery):
    """نمایش خزانه کلن"""
    player_clan = await db.get_player_clan(callback.from_user.id)
    
    if not player_clan:
        await callback.answer("❌ شما عضو کلنی نیستید!")
        return
    
    text = (
        f"💰 خزانه کلن {player_clan['name']}\n\n"
        f" موجودی: {player_clan['treasury']:,} سکه\n\n"
        f"💡 می‌توانید پول به خزانه کلن واریز کنید."
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💎 واریز ۱,۰۰۰,۰۰۰", callback_data="clan_donate_1000000")],
        [types.InlineKeyboardButton(text="💎 واریز ۵,۰۰۰,۰۰۰", callback_data="clan_donate_5000000")],
        [types.InlineKeyboardButton(text="💎 واریز ۱۰,۰۰۰,۰۰۰", callback_data="clan_donate_10000000")],
        [types.InlineKeyboardButton(text="🔙 بازگشت", callback_data="clan_menu")],
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)


async def process_clan_donate(callback: types.CallbackQuery):
    """پردازش واریز به خزانه کلن"""
    data = callback.data
    parts = data.split("_")
    if len(parts) < 3:
        return
    
    amount = int(parts[2])
    
    player = await db.get_player(callback.from_user.id)
    player_clan = await db.get_player_clan(callback.from_user.id)
    
    if not player_clan:
        return
    
    if player['money'] < amount:
        await callback.answer("❌ موجودی کافی نیست!")
        return
    
    await db.update_player_money(callback.from_user.id, -amount)
    await db.update_clan_treasury(player_clan['id'], amount)
    
    await callback.answer(f"✅ {amount:,} سکه به خزانه کلن واریز شد!")
    await show_clan_treasury(callback)


async def show_clan_upgrade(callback: types.CallbackQuery):
    """ارتقای ظرفیت کلن"""
    player_clan = await db.get_player_clan(callback.from_user.id)
    
    if not player_clan:
        return
    
    if player_clan['max_members'] >= config.MAX_CLAN_SIZE:
        await callback.answer("❌ به حداکثر ظرفیت رسیده‌اید!")
        return
    
    cost = config.CLAN_UPGRADE_COST_PER_SLOT
    new_max = player_clan['max_members'] + 1
    
    text = (
        f"💎 ارتقای ظرفیت کلن\n\n"
        f"ظرفیت فعلی: {player_clan['max_members']}\n"
        f"ظرفیت جدید: {new_max}\n"
        f"هزینه: {cost:,} سکه"
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="✅ ارتقا", callback_data=f"confirm_upgrade_{new_max}")],
        [types.InlineKeyboardButton(text="🔙 بازگشت", callback_data="clan_menu")],
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)


async def process_clan_upgrade(callback: types.CallbackQuery):
    """پردازش ارتقای کلن"""
    data = callback.data
    parts = data.split("_")
    if len(parts) < 2:
        return
    
    new_max = int(parts[1])
    cost = config.CLAN_UPGRADE_COST_PER_SLOT
    
    player = await db.get_player(callback.from_user.id)
    player_clan = await db.get_player_clan(callback.from_user.id)
    
    if player['money'] < cost:
        await callback.answer("❌ موجودی کافی نیست!")
        return
    
    await db.update_player_money(callback.from_user.id, -cost)
    await db.upgrade_clan_slots(player_clan['id'], new_max)
    
    await callback.answer(f"✅ ظرفیت کلن به {new_max} نفر ارتقا یافت!")
    await show_clan_menu(callback)


async def process_clan_management(callback: types.CallbackQuery):
    """مدیریت اعضای کلن"""
    data = callback.data
    
    if data.startswith("promote_pm_"):
        user_id = int(data.split("_")[2])
        await db.update_clan_member_role(user_id, "نخست وزیر")
        await callback.answer("✅ ارتقا به نخست وزیر!")
    
    elif data.startswith("demote_general_"):
        user_id = int(data.split("_")[2])
        await db.update_clan_member_role(user_id, "ژنرال ارشد")
        await callback.answer("✅ تنزل به ژنرال ارشد!")
    
    elif data.startswith("transfer_leader_"):
        user_id = int(data.split("_")[2])
        await db.transfer_clan_leadership(callback.from_user.id, user_id)
        await callback.answer("✅ رهبری منتقل شد!")
    
    elif data.startswith("kick_member_"):
        user_id = int(data.split("_")[2])
        await db.leave_clan(user_id)
        await callback.answer("✅ عضو حذف شد!")
    
    await show_clan_members(callback)


# ═══════════════════════════════════════════════════════════
# کمک نظامی
# ═══════════════════════════════════════════════════════════

async def show_military_aid_menu(callback: types.CallbackQuery):
    """نمایش منوی کمک نظامی"""
    player = await db.get_player(callback.from_user.id)
    
    can_aid = await db.can_send_military_aid(callback.from_user.id)
    
    text = (
        "🤝 کمک نظامی\n\n"
        "می‌توانید به بازیکنان دیگر کمک کنید.\n\n"
        f"💰 حداکثر انتقال پول: {config.MILITARY_AID_DAILY_LIMIT_MONEY:,} سکه\n"
        f"⚔️ حداکثر انتقال تجهیزات: {config.MILITARY_AID_DAILY_LIMIT_EQUIPMENT} عدد\n\n"
        f"📊 انتقال‌های امروز: {'در دسترس' if can_aid else 'محدود شده'}"
    )
    
    await callback.message.edit_text(text, reply_markup=get_military_aid_menu_keyboard())


async def show_aid_send_money(callback: types.CallbackQuery, state: FSMContext):
    """ارسال پول"""
    await callback.message.edit_text(
        "💰 مبلغ مورد نظر را وارد کنید:\n\n"
        f"حداکثر: {config.MILITARY_AID_DAILY_LIMIT_MONEY:,} سکه",
        reply_markup=get_back_to_main_keyboard()
    )
    await state.set_state(GameStates.waiting_for_aid_money)


async def process_aid_money(message: types.Message, state: FSMContext):
    """پردازش مبلغ کمک"""
    try:
        amount = int(message.text.replace(",", ""))
    except:
        await message.answer("❌ لطفاً عدد معتبر وارد کنید.")
        return
    
    if amount <= 0:
        await message.answer("❌ مبلغ باید بیشتر از صفر باشد.")
        return
    
    if amount > config.MILITARY_AID_DAILY_LIMIT_MONEY:
        await message.answer(f"❌ حداکثر مبلغ {config.MILITARY_AID_DAILY_LIMIT_MONEY:,} سکه است.")
        return
    
    player = await db.get_player(message.from_user.id)
    if player['money'] < amount:
        await message.answer("❌ موجودی کافی نیست!")
        return
    
    await state.update_data(aid_amount=amount, aid_type="money")
    
    await message.answer(
        "👤 آیدی عددی بازیکن مقصد را وارد کنید:",
        reply_markup=get_back_to_main_keyboard()
    )
    await state.set_state(GameStates.waiting_for_aid_target)


async def process_aid_target(message: types.Message, state: FSMContext):
    """پردازش هدف کمک"""
    try:
        target_id = int(message.text)
    except:
        await message.answer("❌ لطفاً آیدی عددی معتبر وارد کنید.")
        return
    
    target = await db.get_player(target_id)
    if not target:
        await message.answer("❌ بازیکن یافت نشد!")
        return
    
    data = await state.get_data()
    amount = data.get('aid_amount', 0)
    aid_type = data.get('aid_type', 'money')
    
    if aid_type == "money":
        await db.update_player_money(message.from_user.id, -amount)
        await db.update_player_money(target_id, amount)
        await db.record_military_aid(message.from_user.id)
        
        await message.answer(
            f"✅ {amount:,} سکه به {target['country_name']} ارسال شد!",
            reply_markup=get_main_menu_keyboard()
        )
    
    await state.clear()


async def show_aid_send_equipment(callback: types.CallbackQuery, state: FSMContext):
    """ارسال تجهیزات"""
    equipment = await db.get_player_equipment(callback.from_user.id)
    military = [e for e in equipment if e['equipment_type'] == 'military']
    
    if not military:
        await callback.message.edit_text(
            "❌ تجهیزات نظامی ندارید!",
            reply_markup=get_back_to_main_keyboard()
        )
        return
    
    text = "⚔️ تجهیزات نظامی خود را انتخاب کنید:"
    await callback.message.edit_text(text, reply_markup=get_aid_equipment_keyboard(military))


# ═══════════════════════════════════════════════════════════
# گیفت
# ═══════════════════════════════════════════════════════════

async def show_gift_menu(callback: types.CallbackQuery):
    """نمایش منوی گیفت"""
    text = "🎁 ارسال گیفت\n\nیک گزینه را انتخاب کنید:"
    await callback.message.edit_text(text, reply_markup=get_gift_menu_keyboard())


async def show_gift_send_money(callback: types.CallbackQuery, state: FSMContext):
    """ارسال پول"""
    await callback.message.edit_text(
        "💰 مبلغ گیفت را وارد کنید:",
        reply_markup=get_back_to_main_keyboard()
    )
    await state.set_state(GameStates.waiting_for_gift_money)


async def process_gift_money(message: types.Message, state: FSMContext):
    """پردازش مبلغ گیفت"""
    try:
        amount = int(message.text.replace(",", ""))
    except:
        await message.answer("❌ لطفاً عدد معتبر وارد کنید.")
        return
    
    if amount <= 0:
        await message.answer("❌ مبلغ باید بیشتر از صفر باشد.")
        return
    
    player = await db.get_player(message.from_user.id)
    if player['money'] < amount:
        await message.answer("❌ موجودی کافی نیست!")
        return
    
    await state.update_data(gift_amount=amount)
    
    await message.answer(
        "👤 آیدی عددی بازیکن مقصد را وارد کنید:",
        reply_markup=get_back_to_main_keyboard()
    )
    await state.set_state(GameStates.waiting_for_gift_target)


async def process_gift_target(message: types.Message, state: FSMContext):
    """پردازش هدف گیفت"""
    try:
        target_id = int(message.text)
    except:
        await message.answer("❌ لطفاً آیدی عددی معتبر وارد کنید.")
        return
    
    target = await db.get_player(target_id)
    if not target:
        await message.answer("❌ بازیکن یافت نشد!")
        return
    
    data = await state.get_data()
    amount = data.get('gift_amount', 0)
    
    await db.update_player_money(message.from_user.id, -amount)
    await db.update_player_money(target_id, amount)
    await db.send_gift(message.from_user.id, target_id, amount)
    
    await message.answer(
        f"✅ {amount:,} سکه به {target['country_name']} هدیه داده شد!",
        reply_markup=get_main_menu_keyboard()
    )
    
    await state.clear()


# ═══════════════════════════════════════════════════════════
# لیدربورد
# ═══════════════════════════════════════════════════════════

async def show_leaderboard(callback: types.CallbackQuery):
    """نمایش منوی لیدربورد"""
    text = "🏆 لیدربورد\n\nیک گزینه را انتخاب کنید:"
    await callback.message.edit_text(text, reply_markup=get_leaderboard_keyboard())


async def show_player_leaderboard(callback: types.CallbackQuery):
    """لیدربورد بازیکنان"""
    leaderboard = await db.get_leaderboard(100)
    
    if not leaderboard:
        await callback.message.edit_text(
            "❌ هنوز بازیکنی در لیدربورد نیست!",
            reply_markup=get_back_to_main_keyboard()
        )
        return
    
    text = "🏆 لیدربورد بازیکنان (هفتگی)\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    
    for i, player in enumerate(leaderboard[:20], 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        text += f"{medal} {player['country_name']}\n"
        text += f"   🏆 امتیاز: {player['weekly_score']:,}\n"
        text += f"   ⚔️ قدرت: {player['military_power']:,}\n\n"
    
    await callback.message.edit_text(text, reply_markup=get_leaderboard_keyboard())

async def show_clan_leaderboard(callback: types.CallbackQuery):
    """لیدربورد کلن‌ها"""
    clans = await db.get_all_clans_sorted()
    
    if not clans:
        await callback.message.edit_text(
            "❌ هنوز کلنی ساخته نشده!",
            reply_markup=get_back_to_main_keyboard()
        )
        return
    
    text = "👥 لیدربورد کلن‌ها\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    
    for i, clan in enumerate(clans[:10], 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        text += f"{medal} {clan['name']}\n"
        text += f"   👥 اعضا: {clan['member_count']}\n"
        text += f"   ⚔️ قدرت کل: {clan['total_power'] or 0:,}\n\n"
    
    await callback.message.edit_text(text, reply_markup=get_leaderboard_keyboard())


# ═══════════════════════════════════════════════════════════
# دعوت دوستان
# ═══════════════════════════════════════════════════════════

async def show_invite_friends(callback: types.CallbackQuery):
    """دعوت دوستان"""
    player = await db.get_player(callback.from_user.id)
    
    if not player:
        return
    
    bot_username = (await callback.bot.get_me()).username
    invite_link = f"https://t.me/{bot_username}?start={player['invite_code']}"
    
    text = (
        "👥 دعوت دوستان\n\n"
        "لینک اختصاصی خود را برای دوستانتان بفرستید.\n"
        "وقتی دوستتان از این لینک وارد شود، هر دو ۵۰۰,۰۰۰ سکه جایزه می‌گیرید!\n\n"
        f"🔗 لینک دعوت شما:\n{invite_link}\n\n"
        f"📊 تعداد دعوت‌شده‌ها: {await get_invite_count(callback.from_user.id)}"
    )
    
    await callback.message.edit_text(text, reply_markup=get_invite_keyboard(invite_link))


async def get_invite_count(user_id: int) -> int:
    """تعداد افراد دعوت شده"""
    async with aiosqlite.connect(db.DATABASE_PATH) as db_conn:
        cursor = await db_conn.execute(
            "SELECT COUNT(*) FROM players WHERE invited_by = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else 0


# ═══════════════════════════════════════════════════════════
# تجهیزات من
# ═══════════════════════════════════════════════════════════

async def show_my_equipment(callback: types.CallbackQuery):
    """نمایش منوی تجهیزات من"""
    text = "📦 تجهیزات من\n\nیک دسته‌بندی را انتخاب کنید:"
    await callback.message.edit_text(text, reply_markup=get_my_equipment_keyboard())


async def show_my_economic_equipment(callback: types.CallbackQuery):
    """تجهیزات اقتصادی من"""
    equipment = await db.get_player_equipment(callback.from_user.id)
    economic = [e for e in equipment if e['equipment_type'] == 'economic']
    
    if not economic:
        await callback.message.edit_text(
            "❌ تجهیزات اقتصادی ندارید!",
            reply_markup=get_my_equipment_key