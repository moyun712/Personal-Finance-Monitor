"""SavingGoal & GoalMilestone ORM models – savings targets and milestone tracking."""

from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Numeric, Unicode
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class SavingGoal(Base):
    """User-defined savings target with progress tracking.

    status: 1 = in-progress (进行中), 2 = completed (已完成), 3 = abandoned (已放弃)
    """

    __tablename__ = "saving_goals"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(Unicode(100), nullable=False)
    target_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    current_amount: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, server_default="0"
    )
    monthly_saving: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    priority: Mapped[int] = mapped_column(
        TINYINT, nullable=False, comment="1=Highest priority"
    )
    allocation_percent: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True,
        comment="Percentage of annual savings allocated to this goal"
    )
    status: Mapped[int] = mapped_column(
        TINYINT, nullable=False, server_default="1",
        comment="1=InProgress 2=Completed 3=Abandoned"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ──
    user: Mapped["User"] = relationship(back_populates="saving_goals")  # noqa: F821
    milestones: Mapped[list["GoalMilestone"]] = relationship(
        back_populates="goal", lazy="select", cascade="all, delete-orphan"
    )


class GoalMilestone(Base):
    """Intermediate checkpoint within a saving goal.

    status: 1 = pending (待达成 ◎), 2 = in-progress (进行中 →), 3 = completed (已完成 ✓)
    """

    __tablename__ = "goal_milestones"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    goal_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("saving_goals.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Unicode(100), nullable=False)
    target_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[int] = mapped_column(
        TINYINT, nullable=False, server_default="1",
        comment="1=Pending 2=InProgress 3=Completed"
    )

    # ── Relationships ──
    goal: Mapped["SavingGoal"] = relationship(back_populates="milestones")
