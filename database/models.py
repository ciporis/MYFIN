from sqlalchemy import Float, Integer, String, DateTime, func, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fio: Mapped[str] = mapped_column(String)
    phone_number: Mapped[str] = mapped_column(String)

class Operation(Base):
    __tablename__ = "operations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    wallet_id: Mapped[int] = mapped_column(Integer)
    amount: Mapped[float] = mapped_column(Float)
    comment: Mapped[str] = mapped_column(String)
    operation_type: Mapped[str] = mapped_column(String)
    transfer_user_id: Mapped[int] = mapped_column(BigInteger)
    transfer_wallet_id: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(String)

class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    title: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float, default=0)

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    title: Mapped[str] = mapped_column(String)