"""Budget & BudgetPool ORM models – monthly budget configuration and three-pool tracking."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Budget(Base):
    """Monthly budget configuration for a user.

    status: 1 = active (生效中), 2 = settled (已结算)
    """

    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint("user_id", "year_month", name="uq_budgets_user_month"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    year_month: Mapped[str] = mapped_column(
        String(7), nullable=False, comment="Format YYYY-MM, e.g. 2026-03"
    )
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    fixed_amount: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, comment="Fixed pool allocation"
    )
    flexible_amount: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, comment="Flexible pool allocation"
    )
    emergency_amount: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, comment="Emergency pool allocation"
    )
    spread_deduction: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, server_default="0",
        comment="Amount deducted from flexible pool due to spread plans"
    )
    expected_income: Mapped[float | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    status: Mapped[int] = mapped_column(
        TINYINT, nullable=False, server_default="1", comment="1=Active 2=Settled"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ──
    user: Mapped["User"] = relationship(back_populates="budgets")  # noqa: F821
    pools: Mapped[list["BudgetPool"]] = relationship(
        back_populates="budget", lazy="select", cascade="all, delete-orphan"
    )


class BudgetPool(Base):
    """Individual budget pool tracking (one of three per budget).

    pool_type: 1 = Fixed (刚性), 2 = Flexible (弹性), 3 = Emergency (意外)
    """

    __tablename__ = "budget_pools"
    __table_args__ = (
        UniqueConstraint("budget_id", "pool_type", name="uq_budget_pools_budget_type"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    budget_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("budgets.id"), nullable=False
    )
    pool_type: Mapped[int] = mapped_column(
        TINYINT, nullable=False, comment="1=Fixed 2=Flexible 3=Emergency"
    )
    allocated_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    spent_amount: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, server_default="0"
    )
    remaining_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ──
    budget: Mapped["Budget"] = relationship(back_populates="pools")
