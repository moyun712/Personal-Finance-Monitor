"""Tests for Phase 1 Step 1.11 — Full migration validation, seed data & idempotency.

Validates:
  1. All 12 core tables exist in the database.
  2. Preset categories (≥30) with correct pool_type mapping per 需求文档 §6.4.2.
  3. Preset emotion tags (≥15) spanning all 4 dimensions.
  4. Seed script idempotency (re-run produces zero new rows).
  5. All preset categories have user_id=NULL and is_active=True.
  6. Parent-child category hierarchy is intact.

Run with:  cd src/backend && python -m pytest tests/test_phase1_step1_11.py -v
"""

import subprocess
import sys
from decimal import Decimal

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models import (
    AnalysisReport,
    Budget,
    BudgetPool,
    Category,
    EmotionTag,
    GoalMilestone,
    OperationLog,
    SavingGoal,
    SimulationSnapshot,
    SpreadPlan,
    Transaction,
    User,
)


# ── Fixtures ──────────────────────────────────────────────────


@pytest.fixture(scope="module")
def db() -> Session:
    """Provide a database session for the entire test module."""
    session = SessionLocal()
    yield session
    session.close()


# ── Helpers ───────────────────────────────────────────────────


def _get_inspector():
    return inspect(engine)


def _table_columns(table_name: str) -> dict[str, dict]:
    inspector = _get_inspector()
    cols = inspector.get_columns(table_name)
    return {c["name"]: c for c in cols}


# ═══════════════════════════════════════════════════════════════
# 1. All 12 Tables Exist
# ═══════════════════════════════════════════════════════════════


EXPECTED_TABLES = {
    "users",
    "transactions",
    "budgets",
    "budget_pools",
    "categories",
    "saving_goals",
    "goal_milestones",
    "emotion_tags",
    "analysis_reports",
    "simulation_snapshots",
    "operation_logs",
    "spread_plans",
}


class TestAllTablesExist:
    """Verify all 12 core tables are present in the database."""

    def test_all_12_tables_exist(self):
        tables = set(_get_inspector().get_table_names())
        missing = EXPECTED_TABLES - tables
        assert not missing, f"Missing tables: {missing}"

    @pytest.mark.parametrize("table_name", sorted(EXPECTED_TABLES))
    def test_individual_table_exists(self, table_name: str):
        """Each table should be queryable."""
        tables = _get_inspector().get_table_names()
        assert table_name in tables, f"Table '{table_name}' not found"


# ═══════════════════════════════════════════════════════════════
# 2. Preset Categories Validation
# ═══════════════════════════════════════════════════════════════


class TestPresetCategories:
    """Validate preset category seed data per 需求文档 §6.4.2."""

    def test_preset_categories_count_gte_30(self, db: Session):
        """Should have >= 30 preset category records (12 parents + children)."""
        count = db.execute(text(
            "SELECT COUNT(*) FROM categories WHERE user_id IS NULL"
        )).scalar()
        assert count >= 30, f"Expected >= 30 preset categories, got {count}"

    def test_all_preset_user_id_null(self, db: Session):
        """All preset categories should have user_id = NULL."""
        non_null = db.execute(text(
            "SELECT COUNT(*) FROM categories "
            "WHERE user_id IS NOT NULL AND name NOT LIKE 'test_%'"
        )).scalar()
        assert non_null == 0, "Preset categories should have user_id = NULL"

    def test_all_preset_is_active(self, db: Session):
        """All preset categories should have is_active = True."""
        inactive = db.execute(text(
            "SELECT COUNT(*) FROM categories "
            "WHERE user_id IS NULL AND is_active = 0"
        )).scalar()
        assert inactive == 0, "All preset categories should be active"

    def test_10_parent_expense_categories(self, db: Session):
        """10 expense parent categories should exist."""
        expense_parents = [
            "餐饮", "交通", "居住", "通讯", "娱乐",
            "购物", "医疗", "社交", "教育", "金融",
        ]
        for name in expense_parents:
            row = db.execute(text(
                "SELECT id, type FROM categories "
                "WHERE name = :name AND user_id IS NULL AND parent_id IS NULL"
            ), {"name": name}).first()
            assert row is not None, f"Expense parent category '{name}' not found"
            assert row[1] == 1, f"'{name}' type should be 1 (Expense), got {row[1]}"

    def test_2_parent_income_categories(self, db: Session):
        """Income parent categories (工资, 其他收入) should exist with type=2."""
        for name in ["工资", "其他收入"]:
            row = db.execute(text(
                "SELECT type FROM categories "
                "WHERE name = :name AND user_id IS NULL AND parent_id IS NULL"
            ), {"name": name}).first()
            assert row is not None, f"Income parent category '{name}' not found"
            assert row[0] == 2, f"'{name}' type should be 2 (Income), got {row[0]}"

    # ── pool_type mapping per 需求文档 §6.4.2 ────────────────

    def test_housing_rent_is_fixed(self, db: Session):
        """居住-房租 → pool_type=1 (固定/刚性)."""
        row = db.execute(text(
            "SELECT pool_type FROM categories WHERE name = N'房租' AND user_id IS NULL"
        )).first()
        assert row is not None, "Category '房租' not found"
        assert row[0] == 1, f"房租 pool_type should be 1(Fixed), got {row[0]}"

    def test_property_fee_is_fixed(self, db: Session):
        """居住-物业费 → pool_type=1 (固定/刚性)."""
        row = db.execute(text(
            "SELECT pool_type FROM categories WHERE name = N'物业费' AND user_id IS NULL"
        )).first()
        assert row is not None, "Category '物业费' not found"
        assert row[0] == 1, f"物业费 pool_type should be 1(Fixed), got {row[0]}"

    def test_utilities_is_fixed(self, db: Session):
        """居住-水电燃气 → pool_type=1 (固定/刚性)."""
        row = db.execute(text(
            "SELECT pool_type FROM categories WHERE name = N'水电燃气' AND user_id IS NULL"
        )).first()
        assert row is not None, "Category '水电燃气' not found"
        assert row[0] == 1, f"水电燃气 pool_type should be 1(Fixed), got {row[0]}"

    def test_phone_is_fixed(self, db: Session):
        """通讯-话费 → pool_type=1 (固定/刚性)."""
        row = db.execute(text(
            "SELECT pool_type FROM categories WHERE name = N'话费' AND user_id IS NULL"
        )).first()
        assert row is not None, "Category '话费' not found"
        assert row[0] == 1, f"话费 pool_type should be 1(Fixed), got {row[0]}"

    def test_credit_card_is_fixed(self, db: Session):
        """金融-信用卡还款 → pool_type=1 (固定/刚性)."""
        row = db.execute(text(
            "SELECT pool_type FROM categories WHERE name = N'信用卡还款' AND user_id IS NULL"
        )).first()
        assert row is not None, "Category '信用卡还款' not found"
        assert row[0] == 1, f"信用卡还款 pool_type should be 1(Fixed), got {row[0]}"

    def test_insurance_is_fixed(self, db: Session):
        """金融-保险 → pool_type=1 (固定/刚性)."""
        row = db.execute(text(
            "SELECT pool_type FROM categories WHERE name = N'保险' AND user_id IS NULL"
        )).first()
        assert row is not None, "Category '保险' not found"
        assert row[0] == 1, f"保险 pool_type should be 1(Fixed), got {row[0]}"

    def test_dining_takeout_is_flexible(self, db: Session):
        """餐饮-外卖 → pool_type=2 (弹性)."""
        row = db.execute(text(
            "SELECT pool_type FROM categories WHERE name = N'外卖' AND user_id IS NULL"
        )).first()
        assert row is not None, "Category '外卖' not found"
        assert row[0] == 2, f"外卖 pool_type should be 2(Flexible), got {row[0]}"

    def test_transport_taxi_is_flexible(self, db: Session):
        """交通-打车 → pool_type=2 (弹性)."""
        row = db.execute(text(
            "SELECT pool_type FROM categories WHERE name = N'打车' AND user_id IS NULL"
        )).first()
        assert row is not None, "Category '打车' not found"
        assert row[0] == 2, f"打车 pool_type should be 2(Flexible), got {row[0]}"

    def test_entertainment_is_flexible(self, db: Session):
        """娱乐-游戏 → pool_type=2 (弹性)."""
        row = db.execute(text(
            "SELECT pool_type FROM categories WHERE name = N'游戏' AND user_id IS NULL"
        )).first()
        assert row is not None, "Category '游戏' not found"
        assert row[0] == 2, f"游戏 pool_type should be 2(Flexible), got {row[0]}"

    def test_shopping_clothes_is_flexible(self, db: Session):
        """购物-服饰 → pool_type=2 (弹性)."""
        row = db.execute(text(
            "SELECT pool_type FROM categories WHERE name = N'服饰' AND user_id IS NULL"
        )).first()
        assert row is not None, "Category '服饰' not found"
        assert row[0] == 2, f"服饰 pool_type should be 2(Flexible), got {row[0]}"

    def test_medical_clinic_is_emergency(self, db: Session):
        """医疗-门诊 → pool_type=3 (意外)."""
        row = db.execute(text(
            "SELECT pool_type FROM categories WHERE name = N'门诊' AND user_id IS NULL"
        )).first()
        assert row is not None, "Category '门诊' not found"
        assert row[0] == 3, f"门诊 pool_type should be 3(Emergency), got {row[0]}"

    def test_medical_medicine_is_emergency(self, db: Session):
        """医疗-药品 → pool_type=3 (意外)."""
        row = db.execute(text(
            "SELECT pool_type FROM categories WHERE name = N'药品' AND user_id IS NULL"
        )).first()
        assert row is not None, "Category '药品' not found"
        assert row[0] == 3, f"药品 pool_type should be 3(Emergency), got {row[0]}"

    def test_medical_checkup_is_emergency(self, db: Session):
        """医疗-体检 → pool_type=3 (意外)."""
        row = db.execute(text(
            "SELECT pool_type FROM categories WHERE name = N'体检' AND user_id IS NULL"
        )).first()
        assert row is not None, "Category '体检' not found"
        assert row[0] == 3, f"体检 pool_type should be 3(Emergency), got {row[0]}"

    def test_parent_child_hierarchy(self, db: Session):
        """Parent categories should have children linked via parent_id."""
        count = db.execute(text("""
            SELECT COUNT(*) FROM categories c
            INNER JOIN categories p ON c.parent_id = p.id
            WHERE p.user_id IS NULL AND c.user_id IS NULL
        """)).scalar()
        assert count >= 20, (
            f"Expected >= 20 child categories with parents, got {count}"
        )

    def test_each_parent_has_children(self, db: Session):
        """Each expense parent should have at least 2 children."""
        parents = db.execute(text(
            "SELECT id, name FROM categories "
            "WHERE user_id IS NULL AND parent_id IS NULL AND type = 1"
        )).fetchall()
        for pid, pname in parents:
            child_count = db.execute(text(
                "SELECT COUNT(*) FROM categories "
                "WHERE parent_id = :pid AND user_id IS NULL"
            ), {"pid": pid}).scalar()
            assert child_count >= 2, (
                f"Parent '{pname}' should have >= 2 children, got {child_count}"
            )


# ═══════════════════════════════════════════════════════════════
# 3. Preset Emotion Tags Validation
# ═══════════════════════════════════════════════════════════════


class TestPresetEmotionTags:
    """Validate preset emotion tag seed data."""

    def test_preset_tags_count_gte_15(self, db: Session):
        """Should have >= 15 preset emotion tag records."""
        count = db.execute(text(
            "SELECT COUNT(*) FROM emotion_tags WHERE is_system = 1"
        )).scalar()
        assert count >= 15, f"Expected >= 15 preset emotion tags, got {count}"

    def test_all_4_dimensions_present(self, db: Session):
        """Emotion tags should span all 4 dimensions."""
        dims = db.execute(text(
            "SELECT DISTINCT dimension FROM emotion_tags "
            "WHERE is_system = 1 ORDER BY dimension"
        )).fetchall()
        dim_set = {row[0] for row in dims}
        assert dim_set == {1, 2, 3, 4}, (
            f"Expected dimensions {{1,2,3,4}}, got {dim_set}"
        )

    @pytest.mark.parametrize("dim,min_count", [(1, 3), (2, 3), (3, 3), (4, 3)])
    def test_each_dimension_has_enough_tags(self, db: Session, dim: int, min_count: int):
        """Each dimension should have at least 3 tags."""
        count = db.execute(text(
            "SELECT COUNT(*) FROM emotion_tags "
            "WHERE is_system = 1 AND dimension = :dim"
        ), {"dim": dim}).scalar()
        assert count >= min_count, (
            f"Dimension {dim} should have >= {min_count} tags, got {count}"
        )

    def test_specific_tags_exist(self, db: Session):
        """Key emotion tags per plan should exist."""
        expected_tags = [
            "心情不好", "压力大", "焦虑",     # dim 1
            "庆祝", "奖励自己", "开心",       # dim 2
            "随手买的", "习惯了",             # dim 3
            "聚餐", "随份子", "请客",         # dim 4
        ]
        for tag_name in expected_tags:
            row = db.execute(text(
                "SELECT id FROM emotion_tags WHERE name = :name"
            ), {"name": tag_name}).first()
            assert row is not None, f"Emotion tag '{tag_name}' not found"

    def test_all_preset_tags_are_system(self, db: Session):
        """All preset tags should have is_system = True."""
        non_system = db.execute(text(
            "SELECT COUNT(*) FROM emotion_tags WHERE is_system = 0"
        )).scalar()
        assert non_system == 0, (
            f"Expected 0 non-system tags in preset data, got {non_system}"
        )


# ═══════════════════════════════════════════════════════════════
# 4. Seed Script Idempotency
# ═══════════════════════════════════════════════════════════════


class TestSeedIdempotency:
    """Verify that re-running seed_data.py does not create duplicate records."""

    def test_seed_script_idempotent(self, db: Session):
        """Run seed script twice; counts should remain the same."""
        # Record counts before
        cat_before = db.execute(text(
            "SELECT COUNT(*) FROM categories WHERE user_id IS NULL"
        )).scalar()
        tag_before = db.execute(text(
            "SELECT COUNT(*) FROM emotion_tags WHERE is_system = 1"
        )).scalar()

        # Run seed script via subprocess
        result = subprocess.run(
            [sys.executable, "-m", "scripts.seed_data"],
            cwd=str(__import__("pathlib").Path(__file__).resolve().parent.parent),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, (
            f"Seed script failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

        # Verify "Created 0" in output
        assert "Created 0 new categories" in result.stdout, (
            f"Expected 0 new categories on re-run, got: {result.stdout}"
        )
        assert "Created 0 new emotion tags" in result.stdout, (
            f"Expected 0 new emotion tags on re-run, got: {result.stdout}"
        )

        # Verify counts unchanged
        db.expire_all()  # clear session cache
        cat_after = db.execute(text(
            "SELECT COUNT(*) FROM categories WHERE user_id IS NULL"
        )).scalar()
        tag_after = db.execute(text(
            "SELECT COUNT(*) FROM emotion_tags WHERE is_system = 1"
        )).scalar()

        assert cat_after == cat_before, (
            f"Category count changed: {cat_before} → {cat_after}"
        )
        assert tag_after == tag_before, (
            f"Emotion tag count changed: {tag_before} → {tag_after}"
        )


# ═══════════════════════════════════════════════════════════════
# 5. ORM Model Import Completeness
# ═══════════════════════════════════════════════════════════════


class TestModelRegistry:
    """Verify models/__init__.py exports all 12 model classes."""

    def test_all_models_importable(self):
        """All 12 model classes should be importable from app.models."""
        from app import models
        expected_classes = [
            "User", "Category", "Transaction",
            "Budget", "BudgetPool",
            "SavingGoal", "GoalMilestone",
            "EmotionTag", "AnalysisReport",
            "SimulationSnapshot", "OperationLog", "SpreadPlan",
        ]
        for cls_name in expected_classes:
            assert hasattr(models, cls_name), (
                f"app.models missing export: {cls_name}"
            )

    def test_base_metadata_has_all_tables(self):
        """Base.metadata should contain all 12 table names."""
        table_names = set(Base.metadata.tables.keys())
        assert EXPECTED_TABLES.issubset(table_names), (
            f"Missing from Base.metadata: {EXPECTED_TABLES - table_names}"
        )
