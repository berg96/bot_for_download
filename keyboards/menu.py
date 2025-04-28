from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

class MenuCB(CallbackData, prefix='menu'):
    action: str

def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text='Instagram', callback_data=MenuCB(action='instagram'))
    kb.adjust(1)
    return kb


def main_keyboard_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='📷 Instagram')],
            [KeyboardButton(text='ℹ️ Помощь')]
        ],
        resize_keyboard=True
    )
