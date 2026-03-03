"""SimulationSnapshot ORM model – What-if sandbox snapshots for scenario simulation."""

from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Unicode
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class SimulationSnapshot(Base):
    """What-if sandbox snapshot storing simulation parameters and results.

    chosen_plan: the plan number the user chose (NULL if not yet chosen).
    applied: whether the chosen plan has been written back to the real ledger.
    """

    __tablename__ = "simulation_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    base_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="Snapshot baseline date"
    )
    scenario: Mapped[str] = mapped_column(
        Unicode(500), nullable=False, comment="User-provided scenario description"
    )
    snapshot_data: Mapped[str] = mapped_column(
        Unicode(None), nullable=False,
        comment="Full ledger state at base_date (JSON)"
    )
    simulation_params: Mapped[str] = mapped_column(
        Unicode(None), nullable=False,
        comment="Simulation parameter set (JSON)"
    )
    results_json: Mapped[str] = mapped_column(
        Unicode(None), nullable=False,
        comment="Multi-plan simulation results (JSON)"
    )
    chosen_plan: Mapped[int | None] = mapped_column(
        TINYINT, nullable=True,
        comment="User-selected plan number (NULL = not chosen)"
    )
    applied: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="0",
        comment="Whether the chosen plan has been applied to real ledger"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # ── Relationships ──
    user: Mapped["User"] = relationship(back_populates="simulation_snapshots")  # noqa: F821
