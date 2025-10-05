from aiogram.types import InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_callback_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (1, 1,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        if data.startswith('http'):
            keyboard.add(InlineKeyboardButton(text=text, url=data))
        elif data.startswith('webapp:'):
            # Web App кнопка (открывает сайт в Telegram)
            web_app_url = data.replace('webapp:', '', 1)
            keyboard.add(InlineKeyboardButton(
                text=text,
                web_app=WebAppInfo(url=web_app_url)
            ))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()