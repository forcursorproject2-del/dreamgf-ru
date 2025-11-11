from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Get main reply keyboard"""
    keyboard = [
        [KeyboardButton(text="/start"), KeyboardButton(text="/vip")],
        [KeyboardButton(text="/newcharacter")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """Get admin reply keyboard"""
    keyboard = [
        [KeyboardButton(text="/stats"), KeyboardButton(text="/broadcast")],
        [KeyboardButton(text="/ban")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
