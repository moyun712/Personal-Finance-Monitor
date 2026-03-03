"""User ORM model – stores account credentials and profile settings."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, Numeric, String, Unicode
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """System user – one row per registered account."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str | None] = mapped_column(Unicode(50), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    monthly_income: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    payday: Mapped[int | None] = mapped_column(TINYINT, nullable=True, comment="Pay day of month (1-31)")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships (lazy-loaded, defined here to enable back-references) ──
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        back_populates="user", lazy="select"
    )
    budgets: Mapped[list["Budget"]] = relationship(  # noqa: F821
        back_populates="user", lazy="select"
    )
    categories: Mapped[list["Category"]] = relationship(  # noqa: F821
        back_populates="user", lazy="select"
    )
    saving_goals: Mapped[list["SavingGoal"]] = relationship(  # noqa: F821
        back_populates="user", lazy="select"
    )
    analysis_reports: Mapped[list["AnalysisReport"]] = relationship(  # noqa: F821
        back_populates="user", lazy="select"
    )
    simulation_snapshots: Mapped[list["SimulationSnapshot"]] = relationship(  # noqa: F821
        back_populates="user", lazy="select"
    )
    operation_logs: Mapped[list["OperationLog"]] = relationship(  # noqa: F821
        back_populates="user", lazy="select"
    )
    spread_plans: Mapped[list["SpreadPlan"]] = relationship(  # noqa: F821
        back_populates="user", lazy="select"
    )
