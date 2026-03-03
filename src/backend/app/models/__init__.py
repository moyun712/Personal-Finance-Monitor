"""ORM model registry – import all models so Base.metadata is fully populated.

Alembic's env.py imports this package to discover models for autogenerate.
"""

from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.budget import Budget, BudgetPool
from app.models.saving_goal import SavingGoal, GoalMilestone
from app.models.emotion_tag import EmotionTag
from app.models.analysis_report import AnalysisReport
from app.models.simulation_snapshot import SimulationSnapshot
from app.models.operation_log import OperationLog
from app.models.spread_plan import SpreadPlan

__all__ = [
    "User",
    "Category",
    "Transaction",
    "Budget",
    "BudgetPool",
    "SavingGoal",
    "GoalMilestone",
    "EmotionTag",
    "AnalysisReport",
    "SimulationSnapshot",
    "OperationLog",
    "SpreadPlan",
]
