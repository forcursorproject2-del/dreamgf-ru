from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self):
        return self.async_session()

    async def get_active_users(self):
        """Get users active in last 7 days"""
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=7)
        async with self.async_session() as session:
            result = await session.execute(
                "SELECT id FROM users WHERE last_active > :cutoff",
                {"cutoff": cutoff}
            )
            return [row[0] for row in result.fetchall()]

    async def get_user(self, user_id: int):
        async with self.async_session() as session:
            result = await session.execute(
                "SELECT * FROM users WHERE id = :user_id",
                {"user_id": user_id}
            )
            return result.fetchone()

    async def update_user_activity(self, user_id: int):
        async with self.async_session() as session:
            await session.execute(
                "UPDATE users SET last_active = NOW() WHERE id = :user_id",
                {"user_id": user_id}
            )
            await session.commit()

    async def save_payment(self, payment_data: dict):
        async with self.async_session() as session:
            await session.execute(
                """
                INSERT INTO payments (id, user_id, amount, currency, status, description)
                VALUES (:id, :user_id, :amount, :currency, :status, :description)
                """,
                payment_data
            )
            await session.commit()

    async def update_payment_status(self, payment_id: str, status: str):
        async with self.async_session() as session:
            await session.execute(
                "UPDATE payments SET status = :status, paid_at = NOW() WHERE id = :payment_id",
                {"status": status, "payment_id": payment_id}
            )
            await session.commit()

    async def get_chat_history(self, user_id: int, limit: int = 50):
        async with self.async_session() as session:
            result = await session.execute(
                """
                SELECT message, response FROM chat_history
                WHERE user_id = :user_id ORDER BY timestamp DESC LIMIT :limit
                """,
                {"user_id": user_id, "limit": limit}
            )
            return result.fetchall()

    async def save_chat_message(self, user_id: int, character: str, message: str, response: str):
        async with self.async_session() as session:
            await session.execute(
                """
                INSERT INTO chat_history (user_id, character, message, response)
                VALUES (:user_id, :character, :message, :response)
                """,
                {"user_id": user_id, "character": character, "message": message, "response": response}
            )
            await session.commit()
