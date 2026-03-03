"""Tests for Phase 1 Steps 1.6–1.10 — ORM models, migration & seed data validation.

Covers: EmotionTag, AnalysisReport, SimulationSnapshot, OperationLog, SpreadPlan,
        seed data (categories & emotion tags).
Run with:  cd src/backend && python -m pytest tests/test_phase1_step1_6_to_1_10.py -v
"""

import json
from datetime import date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models import (
    AnalysisReport,
    EmotionTag,
    OperationLog,
    SimulationSnapshot,
    SpreadPlan,
    User,
)


# ── Fixtures ──────────────────────────────────────────────────


@pytest.fixture(scope="module")
def db() -> Session:
    """Provide a database session for the entire test module."""
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="module", autouse=True)
def cleanup(db: Session):
    """Delete test data created during this module after all tests finish."""
    yield
    # Clean up in reverse-dependency order
    db.execute(text("DELETE FROM spread_plans WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'test_p1s6_%')"))
    db.execute(text("DELETE FROM operation_logs WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'test_p1s6_%')"))
    db.execute(text("DELETE FROM simulation_snapshots WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'test_p1s6_%')"))
    db.execute(text("DELETE FROM analysis_reports WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'test_p1s6_%')"))
    db.execute(text("DELETE FROM users WHERE username LIKE 'test_p1s6_%'"))
    db.execute(text("DELETE FROM emotion_tags WHERE name LIKE 'test_%'"))
    db.commit()


# ── Helpers ───────────────────────────────────────────────────


def _get_inspector():
    return inspect(engine)


def _table_columns(table_name: str) -> dict[str, dict]:
    inspector = _get_inspector()
    cols = inspector.get_columns(table_name)
    return {c["name"]: c for c in cols}


def _table_indexes(table_name: str) -> list:
    return _get_inspector().get_indexes(table_name)


def _table_foreign_keys(table_name: str) -> list:
    return _get_inspector().get_foreign_keys(table_name)


def _get_or_create_test_user(db: Session) -> User:
    """Get or create a test user for FK-dependent models."""
    user = db.query(User).filter(User.username == "test_p1s6_user").first()
    if user is None:
        user = User(
            username="test_p1s6_user",
            password_hash="$2b$12$fakehashfortest",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


# ═══════════════════════════════════════════════════════════════
# Step 1.6 — EmotionTag model
# ═══════════════════════════════════════════════════════════════


class TestEmotionTagModel:
    """Step 1.6: EmotionTag table schema and ORM operations."""

    def test_emotion_tags_table_exists(self):
        tables = _get_inspector().get_table_names()
        assert "emotion_tags" in tables

    def test_emotion_tags_columns(self):
        cols = _table_columns("emotion_tags")
        expected = {"id", "name", "dimension", "is_system"}
        assert expected.issubset(set(cols.keys()))

    def test_name_unique_constraint(self, db: Session):
        """name column should have a unique constraint."""
        # Insert a test tag
        tag1 = EmotionTag(name="test_unique_tag", dimension=1, is_system=False)
        db.add(tag1)
        db.commit()

        # Try duplicate
        tag2 = EmotionTag(name="test_unique_tag", dimension=2, is_system=False)
        db.add(tag2)
        with pytest.raises(IntegrityError):
            db.flush()
        db.rollback()

    def test_create_and_query_emotion_tag(self, db: Session):
        tag = EmotionTag(name="test_emo_tag_crud", dimension=3, is_system=False)
        db.add(tag)
        db.commit()
        db.refresh(tag)

        assert tag.id is not None
        assert tag.name == "test_emo_tag_crud"
        assert tag.dimension == 3
        assert tag.is_system is False

    def test_is_system_default_true(self, db: Session):
        """is_system should default to True (server_default='1')."""
        # Insert via raw SQL to test server default
        db.execute(text(
            "INSERT INTO emotion_tags (name, dimension) VALUES ('test_default_sys', 1)"
        ))
        db.commit()
        tag = db.query(EmotionTag).filter(EmotionTag.name == "test_default_sys").first()
        assert tag is not None
        assert tag.is_system is True


# ═══════════════════════════════════════════════════════════════
# Step 1.7 — AnalysisReport model
# ═══════════════════════════════════════════════════════════════


class TestAnalysisReportModel:
    """Step 1.7: AnalysisReport table schema and ORM operations."""

    def test_analysis_reports_table_exists(self):
        tables = _get_inspector().get_table_names()
        assert "analysis_reports" in tables

    def test_analysis_reports_columns(self):
        cols = _table_columns("analysis_reports")
        expected = {
            "id", "user_id", "report_type", "period_start", "period_end",
            "ai_role", "summary", "health_score", "detail_json",
            "prompt_used", "skills_invoked", "generated_at"
        }
        assert expected.issubset(set(cols.keys()))

    def test_user_id_fk(self):
        fks = _table_foreign_keys("analysis_reports")
        user_fk = [fk for fk in fks if fk["referred_table"] == "users"]
        assert len(user_fk) == 1

    def test_health_score_nullable(self):
        cols = _table_columns("analysis_reports")
        assert cols["health_score"]["nullable"] is True

    def test_create_weekly_report(self, db: Session):
        user = _get_or_create_test_user(db)
        detail = json.dumps({
            "daily_breakdown": [100, 200, 150, 80, 300, 120, 90],
            "top_categories": ["餐饮", "交通"],
            "suggestions": ["减少外卖频次"]
        })
        report = AnalysisReport(
            user_id=user.id,
            report_type=1,  # weekly
            period_start=date(2026, 2, 24),
            period_end=date(2026, 3, 2),
            ai_role="behavior_doctor",
            summary="本周消费总额 ¥1,040，日均 ¥148.6，比上周增长 12%。",
            health_score=None,  # weekly reports don't have health_score
            detail_json=detail,
            prompt_used="weekly_diagnosis",
            skills_invoked=json.dumps(["SK-01", "SK-02", "SK-03"]),
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        assert report.id is not None
        assert report.report_type == 1
        assert report.ai_role == "behavior_doctor"
        assert report.health_score is None
        assert report.generated_at is not None

    def test_create_yearly_report_with_health_score(self, db: Session):
        user = _get_or_create_test_user(db)
        report = AnalysisReport(
            user_id=user.id,
            report_type=3,  # yearly
            period_start=date(2025, 1, 1),
            period_end=date(2025, 12, 31),
            ai_role="life_planner",
            summary="2025 年度财务健康评估：整体良好，储蓄率 28%。",
            health_score=78,
            detail_json=json.dumps({"savings_rate": 0.28, "goals_achieved": 2}),
            prompt_used="yearly_insight",
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        assert report.health_score == 78
        assert report.report_type == 3

    def test_large_detail_json(self, db: Session):
        """detail_json should handle large JSON text (NVARCHAR(MAX))."""
        user = _get_or_create_test_user(db)
        large_data = json.dumps({"entries": [{"day": i, "amount": i * 10} for i in range(1000)]})
        report = AnalysisReport(
            user_id=user.id,
            report_type=2,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            ai_role="structure_analyst",
            summary="月报测试",
            detail_json=large_data,
            prompt_used="monthly_structure",
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        loaded = json.loads(report.detail_json)
        assert len(loaded["entries"]) == 1000


# ═══════════════════════════════════════════════════════════════
# Step 1.8 — SimulationSnapshot model
# ═══════════════════════════════════════════════════════════════


class TestSimulationSnapshotModel:
    """Step 1.8: SimulationSnapshot table schema and ORM operations."""

    def test_simulation_snapshots_table_exists(self):
        tables = _get_inspector().get_table_names()
        assert "simulation_snapshots" in tables

    def test_simulation_snapshots_columns(self):
        cols = _table_columns("simulation_snapshots")
        expected = {
            "id", "user_id", "base_date", "scenario", "snapshot_data",
            "simulation_params", "results_json", "chosen_plan", "applied", "created_at"
        }
        assert expected.issubset(set(cols.keys()))

    def test_user_id_fk(self):
        fks = _table_foreign_keys("simulation_snapshots")
        user_fk = [fk for fk in fks if fk["referred_table"] == "users"]
        assert len(user_fk) == 1

    def test_chosen_plan_nullable(self):
        cols = _table_columns("simulation_snapshots")
        assert cols["chosen_plan"]["nullable"] is True

    def test_applied_default_false(self, db: Session):
        """applied should default to False (server_default='0')."""
        user = _get_or_create_test_user(db)
        snapshot = SimulationSnapshot(
            user_id=user.id,
            base_date=date(2026, 3, 1),
            scenario="如果我把娱乐支出减少 50%",
            snapshot_data=json.dumps({"budget": {"total": 8000}}),
            simulation_params=json.dumps({"reduce_entertainment": 50}),
            results_json=json.dumps({"plan_a": {"saved": 800}, "plan_b": {"saved": 400}}),
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)

        assert snapshot.applied is False
        assert snapshot.chosen_plan is None
        assert snapshot.created_at is not None

    def test_large_json_fields(self, db: Session):
        """NVARCHAR(MAX) fields should handle large JSON payloads."""
        user = _get_or_create_test_user(db)
        large_snapshot = json.dumps({
            "transactions": [{"id": i, "amount": i * 10.5} for i in range(2000)],
            "budgets": {"total": 10000, "pools": [1, 2, 3]}
        })
        snapshot = SimulationSnapshot(
            user_id=user.id,
            base_date=date(2026, 3, 3),
            scenario="大数据量测试",
            snapshot_data=large_snapshot,
            simulation_params=json.dumps({}),
            results_json=json.dumps({"plans": []}),
            chosen_plan=1,
            applied=False,
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)

        loaded = json.loads(snapshot.snapshot_data)
        assert len(loaded["transactions"]) == 2000


# ═══════════════════════════════════════════════════════════════
# Step 1.9 — OperationLog model
# ═══════════════════════════════════════════════════════════════


class TestOperationLogModel:
    """Step 1.9: OperationLog table schema and ORM operations."""

    def test_operation_logs_table_exists(self):
        tables = _get_inspector().get_table_names()
        assert "operation_logs" in tables

    def test_operation_logs_columns(self):
        cols = _table_columns("operation_logs")
        expected = {
            "id", "user_id", "operation_type", "target_entity", "target_id",
            "before_snapshot", "after_snapshot", "trigger_source",
            "agent_session_id", "is_rolled_back", "created_at"
        }
        assert expected.issubset(set(cols.keys()))

    def test_user_id_fk(self):
        fks = _table_foreign_keys("operation_logs")
        user_fk = [fk for fk in fks if fk["referred_table"] == "users"]
        assert len(user_fk) == 1

    def test_is_rolled_back_default_false(self, db: Session):
        """is_rolled_back should default to False (server_default='0')."""
        user = _get_or_create_test_user(db)
        log = OperationLog(
            user_id=user.id,
            operation_type="budget.modify",
            target_entity="Budget",
            target_id=999,
            before_snapshot=json.dumps({"flexible_amount": 3000}),
            after_snapshot=json.dumps({"flexible_amount": 2500}),
            trigger_source="agent_confirmed",
            agent_session_id="session-abc-123",
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        assert log.id is not None
        assert log.is_rolled_back is False
        assert log.created_at is not None
        assert log.agent_session_id == "session-abc-123"

    def test_create_user_manual_log(self, db: Session):
        user = _get_or_create_test_user(db)
        log = OperationLog(
            user_id=user.id,
            operation_type="goal.adjust_timeline",
            target_entity="SavingGoal",
            target_id=42,
            before_snapshot=json.dumps({"target_date": "2026-12-31"}),
            after_snapshot=json.dumps({"target_date": "2027-03-31"}),
            trigger_source="user_manual",
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        assert log.trigger_source == "user_manual"
        assert log.agent_session_id is None

    def test_snapshot_content_integrity(self, db: Session):
        """before_snapshot and after_snapshot should preserve full JSON content."""
        user = _get_or_create_test_user(db)
        before = {"total_amount": 8000, "pools": [
            {"type": 1, "allocated": 3000, "spent": 1200},
            {"type": 2, "allocated": 3500, "spent": 800},
            {"type": 3, "allocated": 1500, "spent": 0},
        ]}
        after = {**before, "pools": [
            {"type": 1, "allocated": 3000, "spent": 1200},
            {"type": 2, "allocated": 3000, "spent": 800},  # reduced
            {"type": 3, "allocated": 2000, "spent": 0},    # increased
        ]}
        log = OperationLog(
            user_id=user.id,
            operation_type="budget.emergency_spread",
            target_entity="Budget",
            target_id=100,
            before_snapshot=json.dumps(before),
            after_snapshot=json.dumps(after),
            trigger_source="system_auto",
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        loaded_before = json.loads(log.before_snapshot)
        loaded_after = json.loads(log.after_snapshot)
        assert loaded_before["total_amount"] == 8000
        assert len(loaded_after["pools"]) == 3


# ═══════════════════════════════════════════════════════════════
# Step 1.10 — SpreadPlan model
# ═══════════════════════════════════════════════════════════════


class TestSpreadPlanModel:
    """Step 1.10: SpreadPlan table schema and ORM operations."""

    def test_spread_plans_table_exists(self):
        tables = _get_inspector().get_table_names()
        assert "spread_plans" in tables

    def test_spread_plans_columns(self):
        cols = _table_columns("spread_plans")
        expected = {
            "id", "user_id", "source_year_month", "total_amount",
            "monthly_deduction", "remaining_months", "total_months",
            "description", "status", "created_at", "updated_at"
        }
        assert expected.issubset(set(cols.keys()))

    def test_user_id_fk(self):
        fks = _table_foreign_keys("spread_plans")
        user_fk = [fk for fk in fks if fk["referred_table"] == "users"]
        assert len(user_fk) == 1

    def test_user_status_index_exists(self):
        indexes = _table_indexes("spread_plans")
        idx = [i for i in indexes
               if set(i.get("column_names", [])) == {"user_id", "status"}]
        assert len(idx) >= 1, "(user_id, status) index should exist"

    def test_status_default_1(self, db: Session):
        """status should default to 1 (InProgress)."""
        user = _get_or_create_test_user(db)
        plan = SpreadPlan(
            user_id=user.id,
            source_year_month="2026-03",
            total_amount=Decimal("3000.00"),
            monthly_deduction=Decimal("500.00"),
            remaining_months=6,
            total_months=6,
            description="空调维修费分摊",
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)

        assert plan.id is not None
        assert plan.status == 1
        assert plan.created_at is not None
        assert plan.updated_at is not None

    def test_create_and_query_spread_plan(self, db: Session):
        user = _get_or_create_test_user(db)
        plan = SpreadPlan(
            user_id=user.id,
            source_year_month="2026-02",
            total_amount=Decimal("1200.00"),
            monthly_deduction=Decimal("400.00"),
            remaining_months=3,
            total_months=3,
            description="突发体检费用分摊",
            status=1,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)

        queried = db.query(SpreadPlan).filter(SpreadPlan.id == plan.id).first()
        assert queried is not None
        assert queried.source_year_month == "2026-02"
        assert float(queried.total_amount) == 1200.00
        assert float(queried.monthly_deduction) == 400.00
        assert queried.remaining_months == 3
        assert queried.total_months == 3

    def test_fk_constraint_invalid_user(self, db: Session):
        """FK should reject non-existent user_id."""
        plan = SpreadPlan(
            user_id=999999,
            source_year_month="2026-03",
            total_amount=Decimal("100.00"),
            monthly_deduction=Decimal("50.00"),
            remaining_months=2,
            total_months=2,
        )
        db.add(plan)
        with pytest.raises(IntegrityError):
            db.flush()
        db.rollback()


# ═══════════════════════════════════════════════════════════════
# Step 1.11 (partial) — Seed Data Validation
# ═══════════════════════════════════════════════════════════════


class TestSeedData:
    """Validate the seed data populated by scripts/seed_data.py."""

    def test_all_12_tables_exist(self):
        """All 12 core tables should exist in the database."""
        tables = _get_inspector().get_table_names()
        expected_tables = {
            "users", "transactions", "budgets", "budget_pools",
            "categories", "saving_goals", "goal_milestones",
            "emotion_tags", "analysis_reports", "simulation_snapshots",
            "operation_logs", "spread_plans"
        }
        assert expected_tables.issubset(set(tables)), (
            f"Missing tables: {expected_tables - set(tables)}"
        )

    def test_preset_categories_count(self, db: Session):
        """Should have >= 30 preset category records (12 parents + 37 children = 49)."""
        count = db.execute(text(
            "SELECT COUNT(*) FROM categories WHERE user_id IS NULL"
        )).scalar()
        assert count >= 30, f"Expected >= 30 preset categories, got {count}"

    def test_preset_emotion_tags_count(self, db: Session):
        """Should have >= 15 preset emotion tag records."""
        count = db.execute(text(
            "SELECT COUNT(*) FROM emotion_tags WHERE is_system = 1"
        )).scalar()
        assert count >= 15, f"Expected >= 15 preset emotion tags, got {count}"

    def test_preset_categories_user_id_null(self, db: Session):
        """All preset categories should have user_id = NULL."""
        non_null = db.execute(text(
            "SELECT COUNT(*) FROM categories WHERE user_id IS NOT NULL AND name NOT LIKE 'test_%'"
        )).scalar()
        assert non_null == 0, "Preset categories should have user_id = NULL"

    def test_preset_categories_is_active(self, db: Session):
        """All preset categories should have is_active = True."""
        inactive = db.execute(text(
            "SELECT COUNT(*) FROM categories WHERE user_id IS NULL AND is_active = 0"
        )).scalar()
        assert inactive == 0, "All preset categories should be active"

    def test_housing_rent_is_fixed(self, db: Session):
        """居住-房租 should have pool_type=1 (Fixed)."""
        row = db.execute(text(
            "SELECT pool_type FROM categories WHERE name = N'房租' AND user_id IS NULL"
        )).first()
        assert row is not None, "Category '房租' not found"
        assert row[0] == 1, f"房租 pool_type should be 1(Fixed), got {row[0]}"

    def test_dining_takeout_is_flexible(self, db: Session):
        """餐饮-外卖 should have pool_type=2 (Flexible)."""
        row = db.execute(text(
            "SELECT pool_type FROM categories WHERE name = N'外卖' AND user_id IS NULL"
        )).first()
        assert row is not None, "Category '外卖' not found"
        assert row[0] == 2, f"外卖 pool_type should be 2(Flexible), got {row[0]}"

    def test_medical_clinic_is_emergency(self, db: Session):
        """医疗-门诊 should have pool_type=3 (Emergency)."""
        row = db.execute(text(
            "SELECT pool_type FROM categories WHERE name = N'门诊' AND user_id IS NULL"
        )).first()
        assert row is not None, "Category '门诊' not found"
        assert row[0] == 3, f"门诊 pool_type should be 3(Emergency), got {row[0]}"

    def test_income_categories_exist(self, db: Session):
        """Income categories (工资, 其他收入) should exist with type=2."""
        for name in ["工资", "其他收入"]:
            row = db.execute(text(
                f"SELECT type FROM categories WHERE name = N'{name}' AND user_id IS NULL AND parent_id IS NULL"
            )).first()
            assert row is not None, f"Income category '{name}' not found"
            assert row[0] == 2, f"'{name}' type should be 2(Income), got {row[0]}"

    def test_emotion_tags_dimensions(self, db: Session):
        """Emotion tags should span all 4 dimensions."""
        dimensions = db.execute(text(
            "SELECT DISTINCT dimension FROM emotion_tags WHERE is_system = 1 ORDER BY dimension"
        )).fetchall()
        dim_set = {row[0] for row in dimensions}
        assert dim_set == {1, 2, 3, 4}, f"Expected dimensions {{1,2,3,4}}, got {dim_set}"

    def test_parent_child_relationship(self, db: Session):
        """Parent categories should have children linked via parent_id."""
        row = db.execute(text("""
            SELECT COUNT(*) FROM categories c
            INNER JOIN categories p ON c.parent_id = p.id
            WHERE p.user_id IS NULL AND c.user_id IS NULL
        """)).scalar()
        assert row >= 20, f"Expected >= 20 child categories with parents, got {row}"
