from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from bot.keyboards.inline import get_character_keyboard, get_vip_keyboard
from db.database import Database
from utils.cache import Cache
import json
import os
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, db: Database, cache: Cache):
    """Handle /start command"""
    try:
        user_id = message.from_user.id

        # Create user if not exists
        await db.get_or_create_user(user_id)

        # Send welcome message
        welcome_text = (
            "Привет, котёнок! 😘\n\n"
            "Я твоя AI-подруга 18+. Выбери персонажа и давай пообщаемся!\n\n"
            "💋 Флирт, секс, ролевые игры — всё что хочешь!\n"
            "🎤 Голосовые сообщения\n"
            "🖼️ Фото по запросу\n\n"
            "Выбери персонажа ниже:"
        )

        # Get characters
        characters = []
        for file in os.listdir("characters"):
            if file.endswith(".json"):
                with open(f"characters/{file}", "r", encoding="utf-8") as f:
                    char = json.load(f)
                    characters.append(char)

        await message.answer(
            welcome_text,
            reply_markup=get_character_keyboard(characters)
        )

    except Exception as e:
        logger.error(f"Start command failed: {e}")
        await message.answer("Извини, что-то пошло не так 😔 Попробуй ещё раз!")

@router.message(Command("vip"))
async def cmd_vip(message: Message):
    """Handle /vip command"""
    vip_text = (
        "💎 VIP Преимущества:\n\n"
        "✅ Безлимит фото\n"
        "✅ Кастом персонаж\n"
        "✅ Без watermark\n\n"
        "Выбери тариф:"
    )

    await message.answer(vip_text, reply_markup=get_vip_keyboard())

@router.message(Command("newcharacter"))
async def cmd_newcharacter(message: Message, db: Database):
    """Handle /newcharacter command (VIP only)"""
    user = await db.get_user(message.from_user.id)
    if not user or not user.is_vip:
        await message.answer("Эта функция только для VIP пользователей! 💎")
        return

    await message.answer(
        "Пришли фото для создания кастом персонажа!\n"
        "Я создам LoRA модель и добавлю нового персонажа."
    )

def register(dp):
    dp.include_router(router)
