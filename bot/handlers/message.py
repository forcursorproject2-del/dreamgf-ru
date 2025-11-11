from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from bot.states.forms import CharacterForm
from db.database import Database
from utils.cache import Cache
from ai.text_llm import TextLLM
from ai.voice_tts import generate_voice
from ai.image_gen import generate_image
from config.settings import RATE_LIMIT, CHAT_HISTORY_LIMIT
from bot.keyboards.inline import get_action_keyboard
import json
import asyncio
import logging

logger = logging.getLogger(__name__)
router = Router()

# Rate limiting
user_last_message = {}

@router.message(F.text & ~F.text.startswith('/'))
async def handle_message(
    message: Message,
    db: Database,
    cache: Cache,
    llm: TextLLM,
    state,
    trial_allowed: bool
):
    """Handle user messages"""
    if not trial_allowed:
        return  # уже отработал middleware

    try:
        user_id = message.from_user.id
        text = message.text

        # Rate limiting
        now = asyncio.get_event_loop().time()
        if user_id in user_last_message:
            if now - user_last_message[user_id] < 60 / RATE_LIMIT:
                await message.answer("Подожди немного, котёнок! Не так быстро 😘")
                return
        user_last_message[user_id] = now

        # Get user and character
        user = await db.get_user(user_id)
        if not user or not user.current_character:
            await message.answer("Сначала выбери персонажа! /start")
            return

        # Load character
        with open(f"characters/{user.current_character}.json", "r", encoding="utf-8") as f:
            character = json.load(f)

        # Get chat history
        history = await cache.get_chat_history(user_id, CHAT_HISTORY_LIMIT)

        # Generate response
        response = await llm.generate_response(text, character, history)

        # Save to history
        await cache.add_to_chat_history(user_id, text, response)

        # Send text response
        await message.answer(response, reply_markup=get_action_keyboard())

        # Auto voice for short responses
        if len(response) < 100:
            voice = await generate_voice(response, character.get('voice', 'xenia'))
            if voice:
                await message.answer_voice(voice)

    except Exception as e:
        logger.error(f"Message handling failed: {e}")
        await message.answer("Извини, что-то пошло не так 😔")

@router.message(F.photo)
async def handle_photo(message: Message, db: Database):
    """Handle photo uploads for custom character"""
    try:
        user = await db.get_user(message.from_user.id)
        if not user or not user.is_vip:
            await message.answer("Только VIP могут создавать кастом персонажей!")
            return

        # Download photo
        photo = message.photo[-1]
        file = await message.bot.download(photo.file_id)

        # TODO: Send to fal.ai for LoRA training
        await message.answer("Фото получено! Создаю кастом персонажа... (в разработке)")

    except Exception as e:
        logger.error(f"Photo handling failed: {e}")

def register(dp):
    dp.include_router(router)
