from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from db.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

class TrialMiddleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        session: AsyncSession = data['session']
        user = await session.get(User, message.from_user.id)

        if not user:
            user = User(id=message.from_user.id,
                       username=message.from_user.username,
                       first_name=message.from_user.first_name)
            session.add(user)
            await session.commit()

        # VIP — пропускаем
        if user.vip_until and user.vip_until > datetime.utcnow():
            data['trial_allowed'] = True
            return

        # Первый раз — разрешаем всё
        if user.trial_messages == 0 and not user.trial_photo_used and not user.trial_voice_used:
            data['trial_allowed'] = True
            return

        # Проверяем лимиты
        text = message.text.lower() if message.text else ""
        is_photo_request = any(word in text for word in ["фото", "покажи", "сиськи", "попк", "голая", "в белье"])
        is_voice_request = message.voice or any(word in text for word in ["голос", "скажи голосом", "озвучь"])

        if user.trial_messages >= 10:
            await message.answer("❌ Триал закончился, котёнок 😘\n"
                                 "Хочешь безлимит + кастом фото каждый день?\n"
                                 "/vip — 990 руб/мес (первые 100 человек — 495 руб со скидкой 50%)")
            data['trial_allowed'] = False
            return

        if is_photo_request and user.trial_photo_used:
            await message.answer("📸 Одно фото в триале, милый 😏\n"
                                 "Хочешь сколько угодно? Стань VIP!\n/vip")
            data['trial_allowed'] = False
            return

        if is_voice_request and user.trial_voice_used:
            await message.answer("🔊 Один голос в триале, красавчик 🥰\n"
                                 "VIP говорит каждый раз + шлёт фотки без водяного знака\n/vip")
            data['trial_allowed'] = False
            return

        data['trial_allowed'] = True

    async def on_post_process_message(self, message: types.Message, data: dict, result):
        if not data.get('trial_allowed', False):
            return

        session: AsyncSession = data['session']
        user = await session.get(User, message.from_user.id)
        if not user or (user.vip_until and user.vip_until > datetime.utcnow()):
            return

        # Считаем использование
        user.trial_messages += 1

        text = message.text.lower() if message.text else ""
        if any(word in text for word in ["фото", "покажи", "сиськи", "попк", "голая"]) and not user.trial_photo_used:
            user.trial_photo_used = True

        if (message.voice or any(word in text for word in ["голос", "озвучь"])) and not user.trial_voice_used:
            user.trial_voice_used = True

        if user.trial_messages >= 10 or (user.trial_photo_used and user.trial_voice_used):
            user.trial_ended = True

        await session.commit()
