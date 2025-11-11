from aiogram import Router, F
from aiogram.types import CallbackQuery
from db.database import Database
from utils.cache import Cache
from ai.image_gen import generate_image
from ai.voice_tts import generate_voice
from bot.keyboards.inline import get_action_keyboard
import json
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data.startswith("char_"))
async def select_character(callback: CallbackQuery, db: Database):
    """Handle character selection"""
    try:
        char_name = callback.data.split("_", 1)[1]

        # Update user character
        await db.update_user_character(callback.from_user.id, char_name)

        # Load character
        with open(f"characters/{char_name}.json", "r", encoding="utf-8") as f:
            character = json.load(f)

        await callback.message.edit_text(
            f"Выбрана {character['name']} {character['age']} лет!\n\n"
            f"Расскажи мне что-нибудь, котёнок 😘",
            reply_markup=get_action_keyboard()
        )

    except Exception as e:
        logger.error(f"Character selection failed: {e}")
        await callback.answer("Ошибка выбора персонажа")

@router.callback_query(F.data == "voice")
async def send_voice(callback: CallbackQuery, db: Database):
    """Send voice message"""
    try:
        user = await db.get_user(callback.from_user.id)
        if not user or not user.current_character:
            await callback.answer("Сначала выбери персонажа!")
            return

        # Load character
        with open(f"characters/{user.current_character}.json", "r", encoding="utf-8") as f:
            character = json.load(f)

        # Generate voice
        text = "Привет, милый! Как дела? 😘"
        voice = await generate_voice(text, character.get('voice', 'xenia'))

        if voice:
            await callback.message.answer_voice(voice)
            await callback.answer("Голос отправлен!")
        else:
            await callback.answer("Ошибка генерации голоса")

    except Exception as e:
        logger.error(f"Voice generation failed: {e}")
        await callback.answer("Ошибка")

@router.callback_query(F.data == "photo")
async def send_photo(callback: CallbackQuery, db: Database, cache: Cache):
    """Send photo"""
    try:
        user = await db.get_user(callback.from_user.id)
        if not user:
            await callback.answer("Сначала зарегистрируйся!")
            return

        # Check limits for non-VIP
        if not user.is_vip:
            photo_count = await cache.get_user_photo_count(callback.from_user.id)
            if photo_count >= 3:
                await callback.answer("Без VIP только 3 фото в день!")
                return

        # Generate photo
        prompt = "красивая русская девушка 18 лет, обнажённая, реалистично"
        image_bytes = await generate_image(prompt, "anya_lora", cache, user.is_vip)

        if image_bytes:
            await callback.message.answer_photo(image_bytes, caption="Твоё фото 😘")
            await cache.increment_photo_count(callback.from_user.id)
            await callback.answer("Фото отправлено!")
        else:
            await callback.answer("Ошибка генерации фото")

    except Exception as e:
        logger.error(f"Photo generation failed: {e}")
        await callback.answer("Ошибка")

@router.callback_query(F.data.startswith("broadcast_"))
async def handle_broadcast(callback: CallbackQuery, db: Database):
    """Handle broadcast options"""
    try:
        broadcast_type = callback.data.split("_", 1)[1]

        if broadcast_type == "text":
            await callback.message.edit_text("Пришли текст для рассылки:")
        elif broadcast_type == "photo":
            await callback.message.edit_text("Пришли фото с подписью для рассылки:")
        elif broadcast_type == "voice":
            await callback.message.edit_text("Пришли голосовое сообщение для рассылки:")

    except Exception as e:
        logger.error(f"Broadcast handling failed: {e}")

def register(dp):
    dp.include_router(router)
