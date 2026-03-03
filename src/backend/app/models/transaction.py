"""Transaction ORM model – individual income / expense records."""

from datetime import date, datetime, time

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    Time,
    Unicode,
)
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Transaction(Base):
    """Single financial transaction (expense or income).

    type:   1 = expense, 2 = income
    source: 1 = manual, 2 = OCR, 3 = voice, 4 = bulk import
    """

    __tablename__ = "transactions"
    __table_args__ = (
        Index("ix_transactions_user_date", "user_id", "transaction_date"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    type: Mapped[int] = mapped_column(
        TINYINT, nullable=False, comment="1=Expense 2=Income"
    )
    amount: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, comment="Always positive"
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=False
    )
    merchant: Mapped[str | None] = mapped_column(Unicode(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Unicode(500), nullable=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    transaction_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    source: Mapped[int] = mapped_column(
        TINYINT, nullable=False, comment="1=Manual 2=OCR 3=Voice 4=BulkImport"
    )
    emotion_tags: Mapped[str | None] = mapped_column(
        Unicode(500), nullable=True, comment="JSON array of emotion tag names"
    )
    is_recurring: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="0"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ──
    user: Mapped["User"] = relationship(back_populates="transactions")  # noqa: F821
    category: Mapped["Category"] = relationship(  # noqa: F821
        back_populates="transactions"
    )
