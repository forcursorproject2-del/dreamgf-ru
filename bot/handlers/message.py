from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from bot.states.forms import CharacterForm
from db.database import Database
from cache import cache
from ai.text_llm import TextLLM
from ai.voice_tts import generate_voice_async
from ai.image_gen import generate_image_async
from cache import cache
from config.settings import RATE_LIMIT, CHAT_HISTORY_LIMIT
from bot.keyboards.inline import get_action_keyboard
import json
import asyncio
import random
import logging

logger = logging.getLogger(__name__)
router = Router()

# Rate limiting
user_last_message = {}

# Список фраз "ищу фото"
SEARCH_PHRASES = [
    "ммм, хочешь фотку? щас поищу 😏",
    "ооо, ты хочешь фото? найду что то интересное  🔥",
    "сейчас, сейчас... где-то тут было... 😈",
    "ммм, хочешь увидеть меня? ищу лучшее... 💋",
    "фото? легко! щас поищу в белье... 😘"
]

REPLY_PHRASES = [
    "вот, нашла! 🔥",
    "нашла самое горячее 😈",
    "держи, котёнок 💋",
    "вот, как просил... 😏",
    "нашла! смотри внимательно 🔥"
]

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

        # Check if photo request
        text_lower = text.lower()
        is_photo_request = any(word in text_lower for word in ["фото", "покажи", "сиськи", "попу", "голая", "в белье"])

        if is_photo_request:
            # Handle photo request with intermediate messages
            await handle_photo_request(message, user, character, cache, db)
            return

        # Generate response
        response = await llm.generate_response(text, character, history)

        # Save to history
        await cache.add_to_chat_history(user_id, text, response)

        # Send text response
        await message.answer(response, reply_markup=get_action_keyboard())

        # Auto voice for short responses
        if len(response) < 100:
            voice = await generate_voice_async(response, character.get('voice', 'xenia'))
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

async def handle_photo_request(message: Message, user, character, cache: Cache, db: Database):
    """Handle photo request with intermediate messages"""
    try:
        user_id = message.from_user.id

        # Check trial limits
        if user.trial_photo_used and not user.is_vip:
            await message.answer("📸 Одно фото в триале, милый 😏\nХочешь сколько угодно? Стань VIP!\n/vip")
            return

        # Check daily limits for non-VIP
        if not user.is_vip:
            photo_count = await cache.get_user_photo_count(user_id)
            if photo_count >= 3:
                await message.answer("Без VIP только 3 фото в день! /vip")
                return

        # Immediately respond with search phrase
        await message.answer(random.choice(SEARCH_PHRASES))

        # Generate prompt based on message
        prompt = f"красивая русская девушка {character['name']} {character['age']} лет, обнажённая, реалистично, {message.text}"

        # Generate image in background
        image_path = await generate_image_async(prompt, f"{user.current_character}_lora", cache, user.is_vip, user)

        if image_path:
            caption = random.choice(REPLY_PHRASES)
            with open(image_path, "rb") as photo:
                await message.answer_photo(photo, caption=caption)

            # Increment counters
            await cache.increment_photo_count(user_id)

            # Generate voice if enabled and trial allows
            if not user.trial_voice_used or user.is_vip:
                voice = await generate_voice_async(caption, character.get('voice', 'xenia'), user)
                if voice:
                    await message.answer_voice(voice)

            # Update trial status
            if not user.is_vip:
                user.trial_photo_used = True
                await db.session.commit()

        else:
            await message.answer("Извини, не смогла найти фотку 😔 Попробуй позже!")

    except Exception as e:
        logger.error(f"Photo request handling failed: {e}")
        await message.answer("Извини, что-то пошло не так 😔")

def register(dp):
    dp.include_router(router)
