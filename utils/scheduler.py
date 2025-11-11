from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from db.database import Database
from ai.voice_tts import generate_voice
from ai.image_gen import generate_image
import logging

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self, bot: Bot, db: Database):
        self.bot = bot
        self.db = db
        self.scheduler = AsyncIOScheduler()

    def start(self):
        """Start the scheduler"""
        self.scheduler.add_job(
            self.morning_message,
            CronTrigger(hour=9, minute=0, timezone="Europe/Moscow")
        )
        self.scheduler.add_job(
            self.evening_message,
            CronTrigger(hour=23, minute=0, timezone="Europe/Moscow")
        )
        self.scheduler.start()
        logger.info("Scheduler started")

    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()

    async def morning_message(self):
        """Send morning messages to active users"""
        try:
            active_users = await self.db.get_active_users()
            for user_id in active_users:
                try:
                    # Get user's current character
                    user = await self.db.get_user(user_id)
                    character = user.current_character if user else 'anya'

                    # Generate voice message
                    voice = await generate_voice(
                        f"Доброе утро, котёнок 😘 Чем займёмся сегодня?",
                        character
                    )

                    # Generate image
                    prompt = f"русская девушка {character} лет в постели утром, реалистично"
                    image = await generate_image(prompt, character)

                    # Send messages
                    await self.bot.send_voice(user_id, voice)
                    await self.bot.send_photo(user_id, image)

                except Exception as e:
                    logger.error(f"Failed to send morning message to {user_id}: {e}")

        except Exception as e:
            logger.error(f"Morning message job failed: {e}")

    async def evening_message(self):
        """Send evening messages to active users"""
        try:
            active_users = await self.db.get_active_users()
            for user_id in active_users:
                try:
                    # Get user's current character
                    user = await self.db.get_user(user_id)
                    character = user.current_character if user else 'anya'

                    # Generate voice message
                    voice = await generate_voice(
                        f"Спокойной ночи, милый 💋 До завтра!",
                        character
                    )

                    # Send message
                    await self.bot.send_voice(user_id, voice)

                except Exception as e:
                    logger.error(f"Failed to send evening message to {user_id}: {e}")

        except Exception as e:
            logger.error(f"Evening message job failed: {e}")
