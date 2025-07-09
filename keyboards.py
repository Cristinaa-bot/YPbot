from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import CITIES

def city_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=city, callback_data=f"city:{city}")]
        for city in CITIES
    ])
