from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

def get_character_keyboard(characters: list) -> InlineKeyboardMarkup:
    """Get character selection keyboard"""
    keyboard = []

    for char in characters:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{char['name']} {char['age']} лет",
                callback_data=f"char_{char['file']}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_vip_keyboard() -> InlineKeyboardMarkup:
    """Get VIP payment keyboard"""
    keyboard = [
        [InlineKeyboardButton(text="💎 30 дней - 990 руб", callback_data="vip_990")],
        [InlineKeyboardButton(text="💎 90 дней - 1690 руб", callback_data="vip_1690")],
        [InlineKeyboardButton(text="💎 365 дней - 2990 руб", callback_data="vip_2990")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_action_keyboard() -> InlineKeyboardMarkup:
    """Get action keyboard for chat"""
    keyboard = [
        [
            InlineKeyboardButton(text="🎤 Голос", callback_data="voice"),
            InlineKeyboardButton(text="🖼️ Фото", callback_data="photo")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_broadcast_keyboard() -> InlineKeyboardMarkup:
    """Get broadcast options keyboard"""
    keyboard = [
        [InlineKeyboardButton(text="📝 Текст", callback_data="broadcast_text")],
        [InlineKeyboardButton(text="🖼️ Фото", callback_data="broadcast_photo")],
        [InlineKeyboardButton(text="🎤 Голос", callback_data="broadcast_voice")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
