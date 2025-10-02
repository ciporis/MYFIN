from string import punctuation

from aiogram import F, types, Router, Bot
from aiogram.filters import Command

from handlers.filters.chat_types import ChatTypeFilter

router = Router()
router.message.filter(ChatTypeFilter(["group", "supergroup"]))
router.edited_message.filter(ChatTypeFilter(["group", "supergroup"]))

@router.message(Command("admin"))
async def get_admins(message: types.Message, bot: Bot):
    chat_id = message.chat.id
    admins_list = await bot.get_chat_administrators(chat_id)

    admins_list = [
        member.user.id
        for member in admins_list
        if member.status == "creator" or member.status == "administrator"
    ]

    bot.my_admins_list = admins_list

    if message.from_user.id in admins_list:
        await message.delete()