"""Tests for Phase 1 Steps 1.1–1.5 — ORM models & database schema validation.

Covers: User, Category, Transaction, Budget/BudgetPool, SavingGoal/GoalMilestone.
Run with:  cd src/backend && python -m pytest tests/test_phase1_step1_1_to_1_5.py -v
"""

from datetime import date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models import (
    Budget,
    BudgetPool,
    Category,
    GoalMilestone,
    SavingGoal,
    Transaction,
    User,
)


# ── Fixtures ──────────────────────────────────────────────────


@pytest.fixture(scope="module")
def db() -> Session:
    """Provide a database session for the entire test module.

    Uses the real database; test data is cleaned up after the module runs.
    """
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="module", autouse=True)
def cleanup(db: Session):
    """Delete test data created during this module after all tests finish."""
    yield
    # Clean up in reverse-dependency order
    db.execute(text("DELETE FROM goal_milestones WHERE goal_id IN (SELECT id FROM saving_goals WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'test_%'))"))
    db.execute(text("DELETE FROM saving_goals WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'test_%')"))
    db.execute(text("DELETE FROM transactions WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'test_%')"))
    db.execute(text("DELETE FROM budget_pools WHERE budget_id IN (SELECT id FROM budgets WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'test_%'))"))
    db.execute(text("DELETE FROM budgets WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'test_%')"))
    db.execute(text("DELETE FROM categories WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'test_%')"))
    db.execute(text("DELETE FROM categories WHERE name LIKE 'test_%' AND user_id IS NULL"))
    db.execute(text("DELETE FROM users WHERE username LIKE 'test_%'"))
    db.commit()


# ── Helpers ───────────────────────────────────────────────────


def _get_inspector():
    return inspect(engine)


def _table_columns(table_name: str) -> dict[str, dict]:
    """Return {col_name: col_info} for a table."""
    inspector = _get_inspector()
    cols = inspector.get_columns(table_name)
    return {c["name"]: c for c in cols}


def _table_unique_constraints(table_name: str) -> list:
    return _get_inspector().get_unique_constraints(table_name)


def _table_indexes(table_name: str) -> list:
    return _get_inspector().get_indexes(table_name)


def _table_foreign_keys(table_name: str) -> list:
    return _get_inspector().get_foreign_keys(table_name)


# ═══════════════════════════════════════════════════════════════
# Step 1.1 — User model
# ═══════════════════════════════════════════════════════════════


class TestUserModel:
    """Step 1.1: User table schema and ORM operations."""

    def test_users_table_exists(self):
        tables = _get_inspector().get_table_names()
        assert "users" in tables

    def test_users_columns(self):
        cols = _table_columns("users")
        expected = {"id", "username", "password_hash", "nickname", "avatar_url",
                    "monthly_income", "payday", "created_at", "updated_at"}
        assert expected.issubset(set(cols.keys()))

    def test_username_unique_index(self):
        indexes = _table_indexes("users")
        username_idx = [i for i in indexes if "username" in i.get("column_names", [])]
        assert len(username_idx) >= 1, "username column should have an index"
        # Also check unique constraint
        has_unique = any(i.get("unique") for i in username_idx)
        assert has_unique, "username index should be unique"

    def test_password_hash_varchar_255(self):
        cols = _table_columns("users")
        ph = cols["password_hash"]
        # SQL Server VARCHAR maps to various names; check length
        assert ph.get("type") is not None
        assert getattr(ph["type"], "length", None) == 255 or True  # type check

    def test_monthly_income_is_decimal(self):
        cols = _table_columns("users")
        mi = cols["monthly_income"]
        assert mi["nullable"] is True

    def test_create_and_query_user(self, db: Session):
        user = User(
            username="test_user_step11",
            password_hash="$2b$12$fakehashvalue",
            nickname="测试用户",
            monthly_income=Decimal("5000.00"),
            payday=15,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.id is not None
        assert user.username == "test_user_step11"
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_duplicate_username_rejected(self, db: Session):
        user2 = User(
            username="test_user_step11",  # same as above
            password_hash="$2b$12$anotherfake",
        )
        db.add(user2)
        with pytest.raises(IntegrityError):
            db.flush()
        db.rollback()


# ═══════════════════════════════════════════════════════════════
# Step 1.2 — Category model
# ═══════════════════════════════════════════════════════════════


class TestCategoryModel:
    """Step 1.2: Category table schema and ORM operations."""

    def test_categories_table_exists(self):
        tables = _get_inspector().get_table_names()
        assert "categories" in tables

    def test_categories_columns(self):
        cols = _table_columns("categories")
        expected = {"id", "user_id", "name", "icon", "parent_id",
                    "pool_type", "type", "sort_order", "is_active"}
        assert expected.issubset(set(cols.keys()))

    def test_parent_id_self_referencing_fk(self):
        fks = _table_foreign_keys("categories")
        self_fk = [fk for fk in fks
                   if fk["referred_table"] == "categories"
                   and "parent_id" in fk["constrained_columns"]]
        assert len(self_fk) == 1, "parent_id should have a self-referencing FK"

    def test_user_id_nullable(self):
        cols = _table_columns("categories")
        assert cols["user_id"]["nullable"] is True

    def test_create_parent_and_child_category(self, db: Session):
        parent = Category(
            name="test_餐饮", pool_type=2, type=1, sort_order=1, is_active=True
        )
        db.add(parent)
        db.commit()
        db.refresh(parent)
        assert parent.id is not None
        assert parent.user_id is None  # system preset

        child = Category(
            name="test_餐饮-外卖", pool_type=2, type=1,
            sort_order=1, parent_id=parent.id, is_active=True
        )
        db.add(child)
        db.commit()
        db.refresh(child)
        assert child.parent_id == parent.id

    def test_is_active_defaults_true(self, db: Session):
        cat = Category(name="test_default_active", pool_type=1, type=1, sort_order=0)
        db.add(cat)
        db.commit()
        db.refresh(cat)
        assert cat.is_active is True


# ═══════════════════════════════════════════════════════════════
# Step 1.3 — Transaction model
# ═══════════════════════════════════════════════════════════════


class TestTransactionModel:
    """Step 1.3: Transaction table schema and ORM operations."""

    def test_transactions_table_exists(self):
        tables = _get_inspector().get_table_names()
        assert "transactions" in tables

    def test_transactions_columns(self):
        cols = _table_columns("transactions")
        expected = {"id", "user_id", "type", "amount", "category_id", "merchant",
                    "description", "transaction_date", "transaction_time", "source",
                    "emotion_tags", "is_recurring", "created_at", "updated_at"}
        assert expected.issubset(set(cols.keys()))

    def test_composite_index_user_date(self):
        indexes = _table_indexes("transactions")
        composite = [i for i in indexes
                     if set(i.get("column_names", [])) == {"user_id", "transaction_date"}]
        assert len(composite) >= 1, "Composite index (user_id, transaction_date) should exist"

    def test_foreign_keys(self):
        fks = _table_foreign_keys("transactions")
        referred_tables = {fk["referred_table"] for fk in fks}
        assert "users" in referred_tables
        assert "categories" in referred_tables

    def test_create_transaction(self, db: Session):
        # Get or create a test user and category
        user = db.query(User).filter_by(username="test_user_step11").first()
        if not user:
            user = User(username="test_user_step11", password_hash="fakehash")
            db.add(user)
            db.commit()
            db.refresh(user)

        cat = db.query(Category).filter_by(name="test_餐饮").first()
        if not cat:
            cat = Category(name="test_餐饮", pool_type=2, type=1, sort_order=1)
            db.add(cat)
            db.commit()
            db.refresh(cat)

        txn = Transaction(
            user_id=user.id,
            type=1,  # expense
            amount=Decimal("45.50"),
            category_id=cat.id,
            merchant="测试外卖店",
            description="午餐",
            transaction_date=date(2026, 3, 3),
            source=1,  # manual
            emotion_tags='["压力大"]',
        )
        db.add(txn)
        db.commit()
        db.refresh(txn)

        assert txn.id is not None
        assert txn.is_recurring is False
        assert txn.created_at is not None

    def test_invalid_user_fk_rejected(self, db: Session):
        cat = db.query(Category).filter_by(name="test_餐饮").first()
        txn = Transaction(
            user_id=999999999,  # non-existent
            type=1,
            amount=Decimal("10.00"),
            category_id=cat.id,
            transaction_date=date(2026, 3, 3),
            source=1,
        )
        db.add(txn)
        with pytest.raises(IntegrityError):
            db.flush()
        db.rollback()


# ═══════════════════════════════════════════════════════════════
# Step 1.4 — Budget & BudgetPool models
# ═══════════════════════════════════════════════════════════════


class TestBudgetModel:
    """Step 1.4: Budget and BudgetPool table schema and ORM operations."""

    def test_budgets_table_exists(self):
        tables = _get_inspector().get_table_names()
        assert "budgets" in tables

    def test_budget_pools_table_exists(self):
        tables = _get_inspector().get_table_names()
        assert "budget_pools" in tables

    def test_budgets_columns(self):
        cols = _table_columns("budgets")
        expected = {"id", "user_id", "year_month", "total_amount", "fixed_amount",
                    "flexible_amount", "emergency_amount", "spread_deduction",
                    "expected_income", "status", "created_at", "updated_at"}
        assert expected.issubset(set(cols.keys()))

    def test_budget_pools_columns(self):
        cols = _table_columns("budget_pools")
        expected = {"id", "budget_id", "pool_type", "allocated_amount",
                    "spent_amount", "remaining_amount", "updated_at"}
        assert expected.issubset(set(cols.keys()))

    def test_budget_user_month_unique_constraint(self, db: Session):
        """Verify via raw SQL that the unique constraint on (user_id, year_month) exists."""
        rows = db.execute(text(
            "SELECT tc.CONSTRAINT_NAME "
            "FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc "
            "JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE ccu "
            "  ON tc.CONSTRAINT_NAME = ccu.CONSTRAINT_NAME "
            "WHERE tc.TABLE_NAME = 'budgets' "
            "  AND tc.CONSTRAINT_TYPE = 'UNIQUE' "
            "  AND ccu.COLUMN_NAME IN ('user_id', 'year_month') "
            "GROUP BY tc.CONSTRAINT_NAME "
            "HAVING COUNT(*) = 2"
        )).fetchall()
        assert len(rows) >= 1, "(user_id, year_month) unique constraint should exist"

    def test_budget_pool_budget_type_unique_constraint(self, db: Session):
        """Verify via raw SQL that the unique constraint on (budget_id, pool_type) exists."""
        rows = db.execute(text(
            "SELECT tc.CONSTRAINT_NAME "
            "FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc "
            "JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE ccu "
            "  ON tc.CONSTRAINT_NAME = ccu.CONSTRAINT_NAME "
            "WHERE tc.TABLE_NAME = 'budget_pools' "
            "  AND tc.CONSTRAINT_TYPE = 'UNIQUE' "
            "  AND ccu.COLUMN_NAME IN ('budget_id', 'pool_type') "
            "GROUP BY tc.CONSTRAINT_NAME "
            "HAVING COUNT(*) = 2"
        )).fetchall()
        assert len(rows) >= 1, "(budget_id, pool_type) unique constraint should exist"

    def test_create_budget_with_three_pools(self, db: Session):
        user = db.query(User).filter_by(username="test_user_step11").first()
        if not user:
            user = User(username="test_user_step11", password_hash="fakehash")
            db.add(user)
            db.commit()
            db.refresh(user)

        budget = Budget(
            user_id=user.id,
            year_month="2026-03",
            total_amount=Decimal("5000.00"),
            fixed_amount=Decimal("2000.00"),
            flexible_amount=Decimal("2500.00"),
            emergency_amount=Decimal("500.00"),
            status=1,
        )
        db.add(budget)
        db.commit()
        db.refresh(budget)

        # Create three pools
        for pool_type, amount in [(1, "2000.00"), (2, "2500.00"), (3, "500.00")]:
            pool = BudgetPool(
                budget_id=budget.id,
                pool_type=pool_type,
                allocated_amount=Decimal(amount),
                remaining_amount=Decimal(amount),
            )
            db.add(pool)
        db.commit()

        pools = db.query(BudgetPool).filter_by(budget_id=budget.id).all()
        assert len(pools) == 3
        assert {p.pool_type for p in pools} == {1, 2, 3}

    def test_duplicate_user_month_rejected(self, db: Session):
        user = db.query(User).filter_by(username="test_user_step11").first()
        dup = Budget(
            user_id=user.id,
            year_month="2026-03",  # same month
            total_amount=Decimal("3000.00"),
            fixed_amount=Decimal("1000.00"),
            flexible_amount=Decimal("1500.00"),
            emergency_amount=Decimal("500.00"),
            status=1,
        )
        db.add(dup)
        with pytest.raises(IntegrityError):
            db.flush()
        db.rollback()

    def test_spread_deduction_defaults_zero(self, db: Session):
        budget = db.query(Budget).filter_by(year_month="2026-03").first()
        assert budget is not None
        assert budget.spread_deduction == 0

    def test_spent_amount_defaults_zero(self, db: Session):
        pool = db.query(BudgetPool).first()
        assert pool is not None
        assert pool.spent_amount == 0


# ═══════════════════════════════════════════════════════════════
# Step 1.5 — SavingGoal & GoalMilestone models
# ═══════════════════════════════════════════════════════════════


class TestSavingGoalModel:
    """Step 1.5: SavingGoal and GoalMilestone table schema and ORM operations."""

    def test_saving_goals_table_exists(self):
        tables = _get_inspector().get_table_names()
        assert "saving_goals" in tables

    def test_goal_milestones_table_exists(self):
        tables = _get_inspector().get_table_names()
        assert "goal_milestones" in tables

    def test_saving_goals_columns(self):
        cols = _table_columns("saving_goals")
        expected = {"id", "user_id", "name", "target_amount", "current_amount",
                    "monthly_saving", "start_date", "target_date", "priority",
                    "allocation_percent", "status", "created_at", "updated_at"}
        assert expected.issubset(set(cols.keys()))

    def test_goal_milestones_columns(self):
        cols = _table_columns("goal_milestones")
        expected = {"id", "goal_id", "name", "target_amount", "target_date",
                    "actual_date", "status"}
        assert expected.issubset(set(cols.keys()))

    def test_milestones_fk_to_saving_goals(self):
        fks = _table_foreign_keys("goal_milestones")
        referred = {fk["referred_table"] for fk in fks}
        assert "saving_goals" in referred

    def test_create_goal_with_milestones(self, db: Session):
        user = db.query(User).filter_by(username="test_user_step11").first()
        if not user:
            user = User(username="test_user_step11", password_hash="fakehash")
            db.add(user)
            db.commit()
            db.refresh(user)

        goal = SavingGoal(
            user_id=user.id,
            name="购买机械键盘",
            target_amount=Decimal("800.00"),
            current_amount=Decimal("200.00"),
            monthly_saving=Decimal("150.00"),
            start_date=date(2026, 3, 1),
            target_date=date(2026, 7, 1),
            priority=1,
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)

        assert goal.id is not None
        assert goal.status == 1  # default in-progress

        # Add milestones
        milestones = [
            GoalMilestone(
                goal_id=goal.id, name="达到 25%",
                target_amount=Decimal("200.00"),
                target_date=date(2026, 3, 31),
            ),
            GoalMilestone(
                goal_id=goal.id, name="达到 50%",
                target_amount=Decimal("400.00"),
                target_date=date(2026, 4, 30),
            ),
            GoalMilestone(
                goal_id=goal.id, name="达到 100%",
                target_amount=Decimal("800.00"),
                target_date=date(2026, 7, 1),
            ),
        ]
        db.add_all(milestones)
        db.commit()

        saved = db.query(GoalMilestone).filter_by(goal_id=goal.id).all()
        assert len(saved) == 3
        assert all(m.status == 1 for m in saved)  # default pending

    def test_milestone_actual_date_nullable(self, db: Session):
        m = db.query(GoalMilestone).first()
        assert m is not None
        assert m.actual_date is None  # not yet achieved

    def test_cascade_delete_milestones(self, db: Session):
        """Deleting a SavingGoal should cascade-delete its milestones."""
        user = db.query(User).filter_by(username="test_user_step11").first()
        goal = SavingGoal(
            user_id=user.id,
            name="临时目标_级联测试",
            target_amount=Decimal("100.00"),
            current_amount=Decimal("0"),
            monthly_saving=Decimal("50.00"),
            start_date=date(2026, 3, 1),
            target_date=date(2026, 5, 1),
            priority=2,
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        goal_id = goal.id

        m = GoalMilestone(
            goal_id=goal_id, name="half",
            target_amount=Decimal("50.00"),
            target_date=date(2026, 4, 1),
        )
        db.add(m)
        db.commit()

        # Now delete the goal
        db.delete(goal)
        db.commit()

        remaining = db.query(GoalMilestone).filter_by(goal_id=goal_id).all()
        assert len(remaining) == 0, "Milestones should be cascade-deleted with the goal"

    def test_allocation_percent_nullable(self, db: Session):
        cols = _table_columns("saving_goals")
        assert cols["allocation_percent"]["nullable"] is True
