import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
YOOKASSA_SHOP_ID = os.getenv('YOOKASSA_SHOP_ID')
YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
REDIS_URL = os.getenv('REDIS_URL')
ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]

# Constants
RATE_LIMIT = 30  # messages per minute for free users
VOICE_TIMEOUT = 25  # seconds
IMAGE_TIMEOUT = 25  # seconds
CHAT_HISTORY_LIMIT = 50  # messages
WATERMARK_TEXT = "DreamGF.ru"
