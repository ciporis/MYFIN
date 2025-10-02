from datetime import date

from sqlalchemy import Float, Integer, String, DateTime, func, BigInteger, Boolean, Date, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=False)
    used_promocode: Mapped[bool] = mapped_column(Boolean, default=False)
    fio: Mapped[str] = mapped_column(String)
    phone_number: Mapped[str] = mapped_column(String)
    sub_end_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)

    current_wallet_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("wallets.id"),
        nullable=True
    )
    current_wallet: Mapped["Wallet"] = relationship(
        "Wallet",
        foreign_keys=[current_wallet_id],
        post_update=True,
        back_populates="user_as_current"
    )
    wallets: Mapped[list["Wallet"]] = relationship(
        "Wallet",
        foreign_keys="Wallet.user_id",
        back_populates="user",
        cascade="all, delete-orphan"
    )

class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float, default=0)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="wallets"
    )
    user_as_current: Mapped["User"] = relationship(
        "User",
        foreign_keys="User.current_wallet_id",
        back_populates="current_wallet"
    )

class Receiver(Base):
    __tablename__ = "receivers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String)

class Operation(Base):
    __tablename__ = "operations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    wallet_id: Mapped[int] = mapped_column(Integer)
    amount: Mapped[float] = mapped_column(Float)
    comment: Mapped[str] = mapped_column(String)
    operation_type: Mapped[str] = mapped_column(String)
    receiver: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    title: Mapped[str] = mapped_column(String)

class Promocode(Base):
    __tablename__ = "promocodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String)
    percent: Mapped[float] = mapped_column(Float)