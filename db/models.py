from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, BigInteger
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    vip_until = Column(DateTime, nullable=True)
    current_character = Column(String(255), default='anya')
    custom_character = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

    # Trial system fields
    trial_messages = Column(Integer, default=0)      # сколько сообщений потратил
    trial_photo_used = Column(Boolean, default=False)
    trial_voice_used = Column(Boolean, default=False)
    trial_ended = Column(Boolean, default=False)     # флаг, что триал кончился

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(String(255), primary_key=True)
    user_id = Column(BigInteger)
    amount = Column(Integer)
    currency = Column(String(10), default='RUB')
    status = Column(String(50))
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)

class Character(Base):
    __tablename__ = 'characters'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    name = Column(String(255))
    age = Column(Integer)
    description = Column(Text)
    lora_path = Column(String(255))
    voice = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    character = Column(String(255))
    message = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
