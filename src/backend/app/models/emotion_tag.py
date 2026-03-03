"""EmotionTag ORM model – emotion dimension tags for transaction tagging."""

from sqlalchemy import Boolean, Integer, Unicode
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EmotionTag(Base):
    """Emotion tag dictionary entry used for tagging transactions.

    Tags are linked to transactions via Transaction.emotion_tags JSON array.
    This table maintains the tag dictionary and dimension classification for
    aggregate analysis (emotion–spending pattern recognition).

    dimension mapping:
        1 = 压力/焦虑 (Stress/Anxiety)
        2 = 快乐/奖励 (Joy/Reward)
        3 = 无聊/习惯 (Boredom/Habit)
        4 = 社交驱动 (Social-driven)
    """

    __tablename__ = "emotion_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        Unicode(30), unique=True, nullable=False, comment="Tag display name"
    )
    dimension: Mapped[int] = mapped_column(
        TINYINT, nullable=False,
        comment="1=Stress/Anxiety 2=Joy/Reward 3=Boredom/Habit 4=Social-driven"
    )
    is_system: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="1",
        comment="True = system preset; False = user-defined"
    )
