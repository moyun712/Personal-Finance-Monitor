"""Category ORM model – expense/income classification with three-pool mapping."""

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, Unicode
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Category(Base):
    """Spending / income category with optional parent for two-level hierarchy.

    pool_type mapping:
        1 = Fixed (刚性)   – non-compressible expenses like rent, utilities
        2 = Flexible (弹性) – adjustable expenses like dining, entertainment
        3 = Emergency (意外) – unpredictable expenses like medical, gifts

    type mapping:
        1 = Expense (支出)
        2 = Income  (收入)
        3 = General (通用)
    """

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True,
        comment="NULL = system preset; non-NULL = user-defined"
    )
    name: Mapped[str] = mapped_column(Unicode(50), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True,
        comment="Self-referencing FK for two-level hierarchy"
    )
    pool_type: Mapped[int] = mapped_column(
        TINYINT, nullable=False, comment="1=Fixed 2=Flexible 3=Emergency"
    )
    type: Mapped[int] = mapped_column(
        TINYINT, nullable=False, comment="1=Expense 2=Income 3=General"
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1")

    # ── Relationships ──
    user: Mapped["User | None"] = relationship(back_populates="categories")  # noqa: F821
    parent: Mapped["Category | None"] = relationship(
        remote_side=[id], back_populates="children", lazy="select"
    )
    children: Mapped[list["Category"]] = relationship(
        back_populates="parent", lazy="select"
    )
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        back_populates="category", lazy="select"
    )
