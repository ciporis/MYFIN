from datetime import datetime, date, timedelta

from pydantic import BaseModel
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from typing import List

from database.models import User, Operation, Wallet, Category, Promocode, Receiver
from services.constants.operations import Operations

async def orm_add_user(session: AsyncSession, user_id: int, fio: str, phone_number: str):
    user: User = User(id=user_id, fio=fio, phone_number=phone_number)
    session.add(user)
    await session.commit()

async def orm_get_user_by_id(session: AsyncSession, user_id: int):
    query = select(User).where(User.id == user_id).options(selectinload(User.current_wallet))
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def orm_get_user_with_wallets(session: AsyncSession, user_id: int):
    query = select(User).where(User.id == user_id).options(selectinload(User.wallets))
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def orm_get_all_users(session: AsyncSession):
    query = select(Operation)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_user_by_phone_number(session: AsyncSession, phone_number: str):
    query = select(User).where(User.phone_number == phone_number)
    result = await session.execute(query)
    return result.scalar()

async def orm_edit_user_fio(session: AsyncSession, user_id: int, fio: str):
    query = update(User).where(User.id == user_id).values(fio=fio)
    await session.execute(query)
    await session.commit()

async def orm_edit_user_is_subscribed(session: AsyncSession, user_id: int, is_subscribed: bool):
    query = update(User).where(User.id == user_id).values(is_subscribed=is_subscribed)
    await session.execute(query)
    await session.commit()

async def orm_edit_user_end_date(session: AsyncSession, user_id: int, sub_end_date: date):
    query = update(User).where(User.id == user_id).values(sub_end_date=sub_end_date)
    await session.execute(query)
    await session.commit()

async def orm_edit_user_used_promocode(session: AsyncSession, user_id: int, used: bool):
    query = update(User).where(User.id == user_id).values(used_promocode=used)
    await session.execute(query)
    await session.commit()

async def orm_edit_user_phone_number(session: AsyncSession, user_id: int, phone_number: str):
    query = update(User).where(User.id == user_id).values(phone_number=phone_number)
    await session.execute(query)
    await session.commit()

async def orm_edit_user_current_wallet_id(session: AsyncSession, user_id: int, current_wallet_id: int):
    query = update(User).where(User.id == user_id).values(current_wallet_id=current_wallet_id)
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

async def orm_delete_operation(session: AsyncSession, operation_id: int):
    query = delete(Operation).where(Operation.id == operation_id)
    await session.execute(query)
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

class OperationSchema(BaseModel):
    id: int
    user_id: int
    wallet_id: int
    amount: float
    comment: str
    operation_type: str
    receiver: str
    category: str

    class Config:
        from_attributes = True


async def orm_get_wallet_operations_from_to_as_json(session: AsyncSession, wallet_id: int, start_date: datetime, end_date: datetime):
    query = select(Operation).where(Operation.wallet_id == wallet_id and start_date <= Operation.created <= end_date)
    result = await session.execute(query)
    operations = result.scalars().all()

    operations_json = [OperationSchema.from_orm(operation).dict() for operation in operations]

    return operations_json

async def orm_get_wallet_operations_for_current_month(session: AsyncSession, wallet_id: int):
    current_month = datetime.now().month
    current_year = datetime.now().year
    start_date = datetime.strptime(f"{current_year}.{current_month}.01", "%Y.%m.%d")
    query = select(Operation).where(Operation.wallet_id == wallet_id and Operation.created >= start_date)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_latest_wallet_operation(session: AsyncSession, wallet_id: int):
    query = (
        select(Operation)
        .where(Operation.wallet_id == wallet_id)
        .order_by(Operation.created.desc())
        .limit(1)
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()



async def orm_get_user_wallets(session: AsyncSession, user_id: int):
    query = select(Wallet).where(Wallet.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_wallet(session: AsyncSession, wallet_id: int):
    query = select(Wallet).where(Wallet.id == wallet_id)
    result = await session.execute(query)
    return result.scalar()

async def orm_get_wallet_by_title(session: AsyncSession, user_id: int, wallet_name: str):
    query = select(Wallet).where((Wallet.user_id == user_id) & (func.lower(Wallet.title) == func.lower(wallet_name)))
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

async def orm_edit_wallet_is_hidden(session: AsyncSession, wallet_id: int, is_hidden: bool):
    query = update(Wallet).where(Wallet.id == wallet_id).values(is_hidden=is_hidden)
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

async def orm_edit_category_title(session: AsyncSession, category_id: int, title: str):
    query = update(Category).where(Category.id == category_id).values(title=title)
    await session.execute(query)
    await session.commit()

async def orm_delete_category(session: AsyncSession, category_id: int):
    query = delete(Category).where(Category.id == category_id)
    await session.execute(query)
    await session.commit()


# PROMOCODES
async def orm_get_all_promocodes(session: AsyncSession):
    query = select(Promocode)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_delete_promocode(session: AsyncSession, promocode_id: int):
    query = delete(Promocode).where(Promocode.id == promocode_id)
    await session.execute(query)
    await session.commit()

async def orm_add_promocode(session, title: str, percent: float):
    promocode = Promocode(title=title, percent=percent)
    session.add(promocode)
    await session.commit()



# RECEIVERS
async def orm_add_receiver(session, user_id: int, name: str):
    receiver = Receiver(user_id=user_id, name=name)
    session.add(receiver)
    await session.commit()

async def orm_get_receiver(session, receiver_id):
    query = select(Receiver).where(Receiver.id == receiver_id)
    result = await session.execute(query)
    return result.scalar()

async def orm_get_receivers(session: AsyncSession, user_id: int):
    query = select(Receiver).where(Receiver.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()