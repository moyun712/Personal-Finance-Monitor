"""AnalysisReport ORM model – AI-generated weekly/monthly/yearly analysis reports."""

from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, String, Unicode
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class AnalysisReport(Base):
    """AI-generated financial analysis report.

    report_type mapping:
        1 = 周报 (Weekly)   – AI role: behavior_doctor
        2 = 月报 (Monthly)  – AI role: structure_analyst
        3 = 年报 (Yearly)   – AI role: life_planner

    health_score: 0-100, only used for yearly reports (report_type=3).
    """

    __tablename__ = "analysis_reports"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    report_type: Mapped[int] = mapped_column(
        TINYINT, nullable=False,
        comment="1=Weekly 2=Monthly 3=Yearly"
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    ai_role: Mapped[str] = mapped_column(
        String(30), nullable=False,
        comment="behavior_doctor / structure_analyst / life_planner"
    )
    summary: Mapped[str] = mapped_column(
        Unicode(None), nullable=False, comment="AI-generated summary text"
    )
    health_score: Mapped[int | None] = mapped_column(
        TINYINT, nullable=True,
        comment="Financial health score 0-100, yearly reports only"
    )
    detail_json: Mapped[str] = mapped_column(
        Unicode(None), nullable=False,
        comment="Full analysis data in JSON format"
    )
    prompt_used: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="MCP Prompt template name used for generation"
    )
    skills_invoked: Mapped[str | None] = mapped_column(
        Unicode(500), nullable=True,
        comment="JSON array of invoked skill IDs for audit"
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # ── Relationships ──
    user: Mapped["User"] = relationship(back_populates="analysis_reports")  # noqa: F821
