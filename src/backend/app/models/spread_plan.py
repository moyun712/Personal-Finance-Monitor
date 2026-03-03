"""SpreadPlan ORM model – emergency expense spread/amortization plans."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Numeric, Unicode
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class SpreadPlan(Base):
    """Emergency expense spread plan for deferred budget deduction.

    When an unexpected large expense occurs, it can be spread across multiple
    months instead of impacting the current month's budget all at once.
    Each month's budget creation checks active spread plans and applies deductions.

    status mapping:
        1 = 进行中 (In-progress)
        2 = 已完成 (Completed)
        3 = 已取消 (Cancelled)
    """

    __tablename__ = "spread_plans"
    __table_args__ = (
        Index("ix_spread_plans_user_status", "user_id", "status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    source_year_month: Mapped[str] = mapped_column(
        "source_year_month",
        Unicode(7), nullable=False,
        comment="Original month that triggered the spread, e.g. 2026-03"
    )
    total_amount: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False,
        comment="Total amount to be spread"
    )
    monthly_deduction: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False,
        comment="Amount deducted from flexible pool each month"
    )
    remaining_months: Mapped[int] = mapped_column(
        TINYINT, nullable=False,
        comment="Remaining months to deduct"
    )
    total_months: Mapped[int] = mapped_column(
        TINYINT, nullable=False,
        comment="Total spread duration in months"
    )
    description: Mapped[str | None] = mapped_column(
        Unicode(200), nullable=True,
        comment="Reason for the spread"
    )
    status: Mapped[int] = mapped_column(
        TINYINT, nullable=False, server_default="1",
        comment="1=InProgress 2=Completed 3=Cancelled"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ──
    user: Mapped["User"] = relationship(back_populates="spread_plans")  # noqa: F821
