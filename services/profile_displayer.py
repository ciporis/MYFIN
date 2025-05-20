from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.orm_query import orm_get_user_by_id
from services.constants.callbacks import CommandsCallbacks
from create_bot import bot
from keyboards.inline import get_callback_btns

async def show_profile(user_id: int, session: AsyncSession):
    user: User = await orm_get_user_by_id(session, user_id)
    fio: str = user.fio
    balance: float = user.balance

    buttons = {
        "Приход 📈": CommandsCallbacks.write_income,
        "Расход 📉": CommandsCallbacks.write_outcome,
        "Перевод": CommandsCallbacks.write_transfer,
        "История операций": CommandsCallbacks.show_operations_history,
    }
    sizes = (2, 1, 1)

    await bot.send_message(chat_id=user_id, text=f"{fio}   |   {balance} руб.", reply_markup=get_callback_btns(
        btns=buttons,
        sizes=sizes,
    ))