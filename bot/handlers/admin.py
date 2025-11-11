from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from db.database import Database
from config.settings import ADMIN_IDS
from bot.keyboards.inline import get_broadcast_keyboard
import logging

logger = logging.getLogger(__name__)
router = Router()

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return str(user_id) in ADMIN_IDS.split(',')

@router.message(Command("stats"))
async def cmd_stats(message: Message, db: Database):
    """Show statistics"""
    if not is_admin(message.from_user.id):
        return

    try:
        # Get stats
        total_users = await db.get_total_users()
        active_users = await db.get_active_users_count()
        total_payments = await db.get_total_payments()
        monthly_revenue = await db.get_monthly_revenue()

        stats_text = (
            f"📊 Статистика:\n\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"🟢 Активных (7 дней): {active_users}\n"
            f"💰 Всего платежей: {total_payments}\n"
            f"💸 Выручка за месяц: {monthly_revenue} руб"
        )

        await message.answer(stats_text)

    except Exception as e:
        logger.error(f"Stats command failed: {e}")

@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    """Start broadcast"""
    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "Выбери тип рассылки:",
        reply_markup=get_broadcast_keyboard()
    )

@router.message(Command("ban"))
async def cmd_ban(message: Message, db: Database):
    """Ban user"""
    if not is_admin(message.from_user.id):
        return

    try:
        # Parse command: /ban user_id
        parts = message.text.split()
        if len(parts) != 2:
            await message.answer("Использование: /ban user_id")
            return

        user_id = int(parts[1])
        await db.ban_user(user_id)
        await message.answer(f"Пользователь {user_id} забанен")

    except ValueError:
        await message.answer("Неверный user_id")
    except Exception as e:
        logger.error(f"Ban command failed: {e}")

def register(dp):
    dp.include_router(router)
