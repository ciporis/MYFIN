from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.reply import remove
from services.constants.callbacks import WalletOperations, ProfileCommands
from database.orm_query import orm_get_wallet, orm_get_wallets
from database.models import Wallet
from keyboards.inline import get_callback_btns

router = Router()

@router.callback_query(F.data.startswith("wallets_page_"))
async def wallets_pagination(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    page = int(callback.data.split("_")[-1])

    wallets = await orm_get_wallets(session, user_id)

    wallet: Wallet = wallets[page - 1]
    wallet_id = wallet.id

    total_wallets = len(wallets)

    if not wallets:
        await callback.answer("У вас нет ни одного кошелька", show_alert=True)
        return

    wallets_per_page = 1
    total_pages = (total_wallets + wallets_per_page - 1) // wallets_per_page
    current_wallet = wallets[page - 1]

    sizes = (2, 2, 2, 1, 1)

    buttons = {
        "Приход": f"{WalletOperations.write_income}_{wallet_id}_{page}",
        "Расход": f"{WalletOperations.write_outcome}_{wallet_id}_{page}",
        "Перевод": f"{WalletOperations.write_transfer}_{wallet_id}_{page}",
        "История операций": f"{WalletOperations.show_operations_history}_{wallet_id}_{page}",
        "⬅️" : f"wallets_page_{page - 1}",
        "➡️" : f"wallets_page_{page + 1}",
        f"{page}/{total_pages}" : "current_page",
        "Назад" : ProfileCommands.show_profile
    }

    if total_wallets == 1:
        del buttons["⬅️"]
        del buttons["➡️"]
        del buttons[f"{page}/{total_pages}"]
        sizes = (2, 2, 1)

    if total_wallets > 1:
        if page == 1:
            del buttons["⬅️"]
            sizes = (2, 2, 1, 1, 1)

        elif page == total_pages:
            del buttons["➡️"]
            sizes = (2, 2, 1, 1, 1)

    await callback.message.edit_text(
        text=f"{current_wallet.title} | {current_wallet.amount} руб.",
        reply_markup=get_callback_btns(
            btns=buttons,
            sizes=sizes
        )
    )

@router.callback_query(F.data == "current_page")
async def current_page(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()