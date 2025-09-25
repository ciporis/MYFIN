from datetime import datetime, date, timedelta

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Operation, Wallet, Category
from services.constants.operations import Operations

async def orm_add_user(session: AsyncSession, user_id: int, fio: str, phone_number: str):
    user: User = User(id=user_id, fio=fio, phone_number=phone_number)
    session.add(user)
    await session.commit()

async def orm_get_user_by_id(session: AsyncSession, user_id: int):
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    return result.scalar()

async def orm_get_user_by_phone_number(session: AsyncSession, phone_number: str):
    query = select(User).where(User.phone_number == phone_number)
    result = await session.execute(query)
    return result.scalar()

async def orm_edit_user_fio(session: AsyncSession, user_id: int, fio: str):
    query = update(User).where(User.id == user_id).values(fio=fio)
    await session.execute(query)
    await session.commit()

async def orm_edit_user_phone_number(session: AsyncSession, user_id: int, phone_number: str):
    query = update(User).where(User.id == user_id).values(phone_number=phone_number)
    await session.execute(query)
    await session.commit()



async def orm_add_operation(session: AsyncSession, user_id: int, wallet_id: int,
                            amount: float, comment: str, operation_type: str,
                            receiver: str, category: str):
    operation = Operation(user_id=user_id,
                          wallet_id=wallet_id,
                          amount=amount,
                          comment=comment,
                          operation_type=operation_type,
                          receiver=receiver,
                          category=category
    )
    session.add(operation)
    await session.commit()

async def orm_get_all_operations(session: AsyncSession, user_id: int):
    query = select(Operation).where(Operation.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_operations_for_period(session: AsyncSession, user_id: int, days: int):
    start_date = datetime.today() - timedelta(days=days)
    query = select(Operation).where(Operation.user_id == user_id and Operation.created >= start_date)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_all_wallet_operations(session: AsyncSession, wallet_id: int):
    query = select(Operation).where(Operation.wallet_id == wallet_id)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_wallet_operations_for_period(session: AsyncSession, wallet_id: int, days: int):
    start_date = datetime.today() - timedelta(days=days)
    query = select(Operation).where(Operation.wallet_id == wallet_id and Operation.created >= start_date)
    result = await session.execute(query)
    return result.scalars().all()



async def orm_get_wallets(session: AsyncSession, user_id: int):
    query = select(Wallet).where(Wallet.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_wallet(session: AsyncSession, wallet_id: int):
    query = select(Wallet).where(Wallet.id == wallet_id)
    result = await session.execute(query)
    return result.scalar()

async def orm_add_wallet(session: AsyncSession, user_id: int, title: str, amount: float):
    wallet = Wallet(user_id=user_id, title=title, amount=amount)
    session.add(wallet)
    await session.commit()

async def orm_edit_wallet_amount(session: AsyncSession, wallet_id: int, amount: float):
    query = update(Wallet).where(Wallet.id == wallet_id).values(amount=amount)
    await session.execute(query)
    await session.commit()

async def orm_delete_wallet(session: AsyncSession, user_id: int, wallet_id: int):
    query = delete(Wallet).where(Wallet.user_id == user_id, Wallet.id == wallet_id)
    await session.execute(query)
    await session.commit()



async def orm_add_category(session, user_id: int, title: str):
    category = Category(user_id=user_id, title=title)
    session.add(category)
    await session.commit()

async def orm_get_all_categories(session: AsyncSession, user_id: int):
    query = select(Category).where(Category.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_category(session: AsyncSession, category_id: int):
    query = select(Category).where(Category.id == category_id)
    result = await session.execute(query)
    return result.scalar()