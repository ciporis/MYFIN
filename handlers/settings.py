from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards.inline import get_callback_btns
from services.constants import callbacks

router = Router()


@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery, state: FSMContext):
    buttons = {
        "FAQ" : callbacks.FAQ,
        "Тех поддержка" : callbacks.support,
        "Категории расходов" : callbacks.outcome_categories,
        "Скрыть счёт" : callbacks.hide_wallet,
        "Премиум" : callbacks.premium,
        "Назад" : callbacks.ProfileCommands.show_profile
    }

    sizes = (2, 2, 1, 1)

    await callback.message.edit_text("Настройки", reply_markup=get_callback_btns(
        btns=buttons,
        sizes=sizes
    ))