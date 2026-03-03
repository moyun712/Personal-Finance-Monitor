"""OperationLog ORM model – audit trail for all write operations."""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Unicode
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class OperationLog(Base):
    """Audit log for write operations executed via MCP Tools or user actions.

    trigger_source values:
        'user_manual'      – direct user action from settings/forms
        'agent_confirmed'  – Agent-generated plan confirmed by user
        'system_auto'      – automatic system action (e.g. monthly budget creation)

    Supports 7-day rollback via before_snapshot / after_snapshot JSON diffs.
    """

    __tablename__ = "operation_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    operation_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="e.g. budget.modify, goal.adjust_timeline, budget.emergency_spread"
    )
    target_entity: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="e.g. Budget, SavingGoal"
    )
    target_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="ID of the operated entity"
    )
    before_snapshot: Mapped[str] = mapped_column(
        Unicode(None), nullable=False,
        comment="Pre-operation data snapshot (JSON)"
    )
    after_snapshot: Mapped[str] = mapped_column(
        Unicode(None), nullable=False,
        comment="Post-operation data snapshot (JSON)"
    )
    trigger_source: Mapped[str] = mapped_column(
        String(30), nullable=False,
        comment="user_manual / agent_confirmed / system_auto"
    )
    agent_session_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
        comment="Agent conversation session ID if triggered by Agent"
    )
    is_rolled_back: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="0",
        comment="Whether this operation has been rolled back"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # ── Relationships ──
    user: Mapped["User"] = relationship(back_populates="operation_logs")  # noqa: F821
