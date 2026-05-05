"""
سیستم زمان‌بندی - پرداخت خودکار سود هر ساعت
"""

import asyncio
from datetime import datetime
from typing import List, Dict
from database import (
    get_all_players_sorted, 
    get_player_equipment, 
    update_player_money,
    get_setting,
    set_setting
)
from equipment import ECONOMIC_EQUIPMENT, ALL_EQUIPMENT


# ═══════════════════════════════════════════════════════════
# محاسبه سود ساعتی
# ═══════════════════════════════════════════════════════════

def calculate_hourly_profit(user_id: int) -> int:
    """
    محاسبه سود ساعتی یک بازیکن بر اساس تجهیزات اقتصادی
    سود روزانه / 24 = سود ساعتی
    """
    return 0  # TODO: از دیتابیس بخوان


async def calculate_player_hourly_profit(user_id: int) -> int:
    """محاسبه سود ساعتی یک بازیکن"""
    equipment = await get_player_equipment(user_id)
    
    total_hourly_profit = 0
    
    for eq in equipment:
        if eq['equipment_type'] == 'economic':
            # دریافت اطلاعات تجهیزات
            eq_info = ALL_EQUIPMENT.get(eq['name'])
            if eq_info:
                # سود روزانه / 24 = سود ساعتی
                daily_profit = eq_info.effect
                hourly_profit = daily_profit // 24
                total_hourly_profit += hourly_profit * eq['quantity']
    
    return total_hourly_profit


async def calculate_all_players_hourly_profit() -> Dict[int, int]:
    """محاسبه سود ساعتی همه بازیکنان"""
    players = await get_all_players_sorted()
    profits = {}
    
    for player in players:
        user_id = player['user_id']
        profit = await calculate_player_hourly_profit(user_id)
        profits[user_id] = profit
    
    return profits


# ═══════════════════════════════════════════════════════════
# پرداخت سود ساعتی
# ═══════════════════════════════════════════════════════════

async def pay_hourly_profits():
    """پرداخت سود ساعتی به همه بازیکنان"""
    profits = await calculate_all_players_hourly_profit()
    
    for user_id, profit in profits.items():
        if profit > 0:
            await update_player_money(user_id, profit)
            print(f"[{datetime.now()}] پرداخت {profit:,} سکه به بازیکن {user_id}")
    
    return len(profits)


# ═══════════════════════════════════════════════════════════
# زمان‌بندی
# ═══════════════════════════════════════════════════════════

async def profit_scheduler(bot, interval_hours: int = 1):
    """
    اجرای زمان‌بند پرداخت سود
    هر interval_hours ساعت یکبار اجرا می‌شود
    """
    interval_seconds = interval_hours * 3600
    
    while True:
        try:
            # ثبت زمان آخرین پرداخت
            now = datetime.now().isoformat()
            await set_setting("last_profit_payment", now)
            
            # پرداخت سود به همه
            count = await pay_hourly_profits()
            print(f"[{now}] پرداخت سود ساعتی به {count} بازیکن انجام شد.")
            
            # ارسال اعلان به بازیکنان
            await notify_players_about_profit(bot, profits)
            
        except Exception as e:
            print(f"خطا در پرداخت سود: {e}")
        
        # انتظار برای اجرای بعدی
        await asyncio.sleep(interval_seconds)


async def notify_players_about_profit(bot, profits: Dict[int, int]):
    """اعلان پرداخت سود به بازیکنان"""
    from aiogram import Bot
    
    for user_id, profit in profits.items():
        if profit > 0:
            try:
                await bot.send_message(
                    user_id,
                    f"💰 سود ساعتی شما واریز شد!\n\n"
                    f"مبلغ: +{profit:,} سکه\n"
                    f"⏰ زمان: {datetime.now().strftime('%H:%M')}"
                )
            except Exception as e:
                print(f"خطا در ارسال اعلان به {user_id}: {e}")


# ═══════════════════════════════════════════════════════════
# ریست هفتگی لیدربورد
# ═══════════════════════════════════════════════════════════

async def weekly_reset_scheduler(bot, interval_days: int = 7):
    """
    زمان‌بند ریست هفتگی لیدربورد
    """
    interval_seconds = interval_days * 24 * 3600
    
    while True:
        try:
            # ریست امتیازات هفتگی
            await reset_weekly_scores()
            
            # ارسال جوایز به برترین‌ها
            await distribute_weekly_rewards(bot)
            
            print(f"[{datetime.now()}] ریست هفتگی لیدربورد انجام شد.")
            
        except Exception as e:
            print(f"خطا در ریست هفتگی: {e}")
        
        await asyncio.sleep(interval_seconds)


async def distribute_weekly_rewards(bot):
    """توزیع جوایز هفتگی"""
    from database import get_leaderboard, get_all_clans_sorted, update_player_money
    from config import INITIAL_MONEY
    
    # جوایز بازیکنان (رتبه 1 تا 100)
    player_rewards = {
        1: 5_000_000,   # رتبه اول
        2: 3_000_000,   # رتبه دوم
        3: 2_000_000,   # رتبه سوم
        4: 1_500_000,
        5: 1_000_000,
    }
    
    # جوایز 6 تا 100 (کاهشی)
    for i in range(6, 101):
        player_rewards[i] = max(100_000, 1_000_000 - (i - 5) * 20_000)
    
    # دریافت لیدربورد
    leaderboard = await get_leaderboard(100)
    
    for rank, player in enumerate(leaderboard, 1):
        if rank in player_rewards:
            reward = player_rewards[rank]
            await update_player_money(player['user_id'], reward)
            
            try:
                await bot.send_message(
                    player['user_id'],
                    f"🏆 تبریک! شما در رتبه {rank} هفتگی قرار گرفتید!\n"
                    f"جایزه: {reward:,} سکه"
                )
            except:
                pass
    
    # جوایز کلن (3 کلن برتر)
    clan_rewards = {
        1: 10_000_000,
        2: 5_000_000,
        3: 2_500_000,
    }
    
    clans = await get_all_clans_sorted()[:3]
    
    for rank, clan in enumerate(clans, 1):
        if rank in clan_rewards:
            reward = clan_rewards[rank]
            # واریز به خزانه کلن
            from database import update_clan_treasury
            await update_clan_treasury(clan['id'], reward)


# ═══════════════════════════════════════════════════════════
# شروع زمان‌بندها
# ═══════════════════════════════════════════════════════════

async def start_schedulers(bot):
    """شروع همه زمان‌بندها"""
    # زمان‌بند پرداخت سود (هر 1 ساعت)
    asyncio.create_task(profit_scheduler(bot, interval_hours=1))
    
    # زمان‌بند ریست هفتگی (هر 7 روز)
    asyncio.create_task(weekly_reset_scheduler(bot, interval_days=7))
    
    print("⏰ زمان‌بندها شروع شدند.")