from aiogram.filters import BaseFilter
from aiogram.types import Message
from db.database import Database
from datetime import datetime

class IsVIPFilter(BaseFilter):
    """Filter for VIP users"""

    async def __call__(self, message: Message, db: Database) -> bool:
        user = await db.get_user(message.from_user.id)
        if not user:
            return False

        return user.is_vip

def register(dp):
    dp.filters_factory.bind(IsVIPFilter, event_handlers=[
        # Add handlers that require VIP here
    ])
