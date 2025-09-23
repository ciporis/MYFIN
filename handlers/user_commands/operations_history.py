import random
from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util.preloaded import orm_descriptor_props

from database.models import Operation, Category, Wallet
from services.constants.callbacks import WalletOperations
from services.constants.operations import Operations
from services.profile_displayer import show_profile
from database.orm_query import orm_get_wallet_operations_for_period, orm_get_all_categories, orm_get_wallet
from keyboards.inline import get_callback_btns

router = Router()

@router.callback_query(F.data == "menu")
async def show_profile_callback(call: CallbackQuery, session: AsyncSession):
    await call.message.delete()
    await show_profile(call.from_user.id, session)

@router.callback_query(F.data.contains(WalletOperations.show_operations_history))
async def show_spens_review(callback: CallbackQuery, session: AsyncSession):
    wallet_id=int(callback.data.split('_')[-2])
    page = int(callback.data.split("_")[-1])
    today: datetime = datetime.today()

    wallet: Wallet = await orm_get_wallet(session, wallet_id)

    operations = await orm_get_wallet_operations_for_period(session, wallet_id, 366)

    if operations:
        await callback.message.edit_text('Загрузка...')

        await callback.answer()

        categories = await orm_get_all_categories(session, callback.from_user.id)

        spends = []
        incomes = []

        for operation in operations:
            operation: Operation
            if operation.operation_type == Operations.OUTCOME.value or operation.operation_type == Operations.TRANSFER_TO.value:
                spends.append(operation)
            elif operation.operation_type == Operations.INCOME.value or operation.operation_type == Operations.TRANSFER_FROM.value:
                incomes.append(operation)

        start_balance = 0

    #     promt = """Проанализируй эти комментарии (id транзакции :  комментарий к транзакции) и сделай вывод по каждому из них к какой категории относится транзакция, на все транзакции максимум 15 категорий
    # Ответ верни в виде JSON файла, где ключ - id транзакции, значение - полученная категория транзакции.\n\n"""

        if len(incomes) == 0 and wallet.amount > 0:
            start_balance = wallet.amount
        else:
            for operation in incomes:
                operation: Operation
                start_balance += operation.amount
                # promt += f"{operation.id} : {operation.comment}\n"

        # comments_categories: dict[str, str] = await openai.get_json_as_map(prompt=promt)
        # unique_categories = set(comments_categories.values())

        categories_coverage: dict[str, int] = {}

        # for category in categories:
        #     category: Category
        #     for operation in spends:
        #         operation: Operation
        #
        #         if categories_coverage.__contains__(operation.category) == False:
        #             categories_coverage[operation.category] = 0
        #             categories_coverage[operation.category] += operation.amount
        #         elif operation.category == category.title:
        #             categories_coverage[operation.category] += operation.amount

        for category in categories:
            category: Category
            categories_coverage[category.title] = 0

        for operation in spends:
            operation: Operation
            categories_coverage[operation.category] += operation.amount


        emoji = ['🟢','🔵','🟠','🟡','🟣','🔴']
        text = "<b>Анализ Расходов</b>\n\n"

        for category in categories_coverage.keys():
            percentage = (categories_coverage[category] / start_balance) * 100
            text += f"{random.choice(emoji)}{category}|{categories_coverage[category]} руб|{percentage:.2f}%\n\n"

        await callback.message.edit_text(text=text, reply_markup=get_callback_btns(
            btns={
                "Назад" : f"wallets_page_{page}"
            }
        ))
    else:
        await callback.message.edit_text(text="Пусто...", reply_markup=get_callback_btns(
            btns={
                "Назад" : f"wallets_page_{page}"
            }
        ))

# @router.callback_query(F.data.contains(WalletOperations.show_operations_history))
# async def show_periods(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
#     await callback.answer()
#     await state.update_data(wallet_id=int(callback.data.split('_')[-1]))
#
#     buttons = {
#         "1 месяц" : "show_history" + "_1",
#         "Квартал" : "show_history" + "_3",
#         "Пол года" : "show_history" + "_6",
#         "Всё время" : "show_history" + "_0"
#     }
#
#     await callback.message.edit_text("Период", reply_markup=get_callback_btns(
#         btns=buttons,
#     ))
#
# @router.callback_query(F.data.contains("show_history"))
# async def show_operations_history(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
#     await callback.answer()
#     state_data = await state.get_data()
#     wallet_id: int = state_data["wallet_id"]
#     months: int = int(callback.data.split('_')[-1])
#
#     text = "Дата   Сумма   Категория"
#
#     if int(months) == 0:
#         operations = await orm_get_all_wallet_operations(session=session, wallet_id=wallet_id)
#     else:
#         operations = await orm_get_wallet_operations_in_period(session, wallet_id, int(months))
#
#     for operation in operations:
#         operation: Operation
#         date: datetime = operation.created
#         text += f"\n{date.day}.{date.month}.{date.year}   {operation.amount}   {operation.category}"
#
#     await callback.message.edit_text(text=text, reply_markup=get_callback_btns(
#         btns={
#             "Назад" : "menu"
#         }
#     ))
#
#     await state.clear()