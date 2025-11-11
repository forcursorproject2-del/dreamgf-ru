from bot.init import dp
from bot.handlers import start, message, payments, admin, callback
from bot.keyboards import inline, reply
from bot.states import forms
from bot.filters import vip
from bot.middlewares.trial import TrialMiddleware
from utils.scheduler import Scheduler
from db.database import Database
from utils.cache import Cache
from ai.text_llm import TextLLM
from ai.voice_tts import load_model
from ai.image_gen import load_pipeline
import asyncio
import logging

logger = logging.getLogger(__name__)

async def setup_services():
    """Initialize all services"""
    try:
        # Initialize database
        db = Database()
        await db.create_tables()

        # Initialize cache
        cache = Cache()

        # Initialize AI services
        llm = TextLLM()
        load_model()  # Load TTS model
        load_pipeline()  # Load image pipeline

        # Initialize scheduler
        scheduler = Scheduler()
        await scheduler.start()

        logger.info("All services initialized")
        return db, cache, llm, scheduler

    except Exception as e:
        logger.error(f"Failed to setup services: {e}")
        raise

def register_handlers():
    """Register all handlers"""
    # Register handlers
    start.register(dp)
    message.register(dp)
    payments.register(dp)
    admin.register(dp)
    callback.register(dp)

    # Register filters
    vip.register(dp)

    logger.info("Handlers registered")

def setup_middlewares(dp):
    """Setup middlewares"""
    dp.middleware.setup(TrialMiddleware())
    logger.info("Middlewares registered")

async def on_startup():
    """Startup function"""
    await setup_services()
    register_handlers()
    setup_middlewares(dp)
    logger.info("Bot started")

async def on_shutdown():
    """Shutdown function"""
    logger.info("Bot stopped")
