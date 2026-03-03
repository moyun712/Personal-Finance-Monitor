"""Seed data script – populate system-preset categories and emotion tags.

Idempotent: safe to run multiple times without creating duplicates.
Run with:  cd src/backend && python -m scripts.seed_data
"""

import sys
import os

# Ensure the backend package is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal
from app.models.category import Category
from app.models.emotion_tag import EmotionTag


# ── Preset Categories ─────────────────────────────────────────
# Format: (name, pool_type, type, sort_order, children)
# pool_type: 1=Fixed 2=Flexible 3=Emergency
# type: 1=Expense 2=Income 3=General
# Children inherit parent's pool_type and type unless overridden.

PRESET_CATEGORIES = [
    # ── 支出分类 ──
    ("餐饮", 2, 1, 10, [
        ("外卖", 2, 1, 11),
        ("堂食", 2, 1, 12),
        ("奶茶咖啡", 2, 1, 13),
        ("食材", 2, 1, 14),
    ]),
    ("交通", 2, 1, 20, [
        ("公交地铁", 2, 1, 21),
        ("打车", 2, 1, 22),
        ("加油", 2, 1, 23),
    ]),
    ("居住", 1, 1, 30, [
        ("房租", 1, 1, 31),
        ("物业费", 1, 1, 32),
        ("水电燃气", 1, 1, 33),
    ]),
    ("通讯", 1, 1, 40, [
        ("话费", 1, 1, 41),
        ("宽带", 1, 1, 42),
    ]),
    ("娱乐", 2, 1, 50, [
        ("游戏", 2, 1, 51),
        ("电影", 2, 1, 52),
        ("KTV", 2, 1, 53),
        ("旅行", 2, 1, 54),
    ]),
    ("购物", 2, 1, 60, [
        ("服饰", 2, 1, 61),
        ("日用品", 2, 1, 62),
        ("电子产品", 2, 1, 63),
        ("美妆", 2, 1, 64),
    ]),
    ("医疗", 3, 1, 70, [
        ("门诊", 3, 1, 71),
        ("药品", 3, 1, 72),
        ("体检", 3, 1, 73),
    ]),
    ("社交", 2, 1, 80, [
        ("聚餐", 2, 1, 81),
        ("随礼", 2, 1, 82),
        ("送礼", 2, 1, 83),
    ]),
    ("教育", 2, 1, 90, [
        ("课程", 2, 1, 91),
        ("书籍", 2, 1, 92),
        ("培训", 2, 1, 93),
    ]),
    ("金融", 1, 1, 100, [
        ("信用卡还款", 1, 1, 101),
        ("保险", 1, 1, 102),
    ]),
    # ── 收入分类 ──
    ("工资", 2, 2, 110, [
        ("月薪", 2, 2, 111),
        ("奖金", 2, 2, 112),
        ("补贴", 2, 2, 113),
    ]),
    ("其他收入", 2, 2, 120, [
        ("兼职", 2, 2, 121),
        ("红包", 2, 2, 122),
        ("退款", 2, 2, 123),
    ]),
]


# ── Preset Emotion Tags ──────────────────────────────────────
# Format: (name, dimension)
# dimension: 1=Stress/Anxiety 2=Joy/Reward 3=Boredom/Habit 4=Social-driven

PRESET_EMOTION_TAGS = [
    # Dimension 1: 压力/焦虑
    ("心情不好", 1),
    ("被骂了", 1),
    ("加班累", 1),
    ("压力大", 1),
    ("焦虑", 1),
    # Dimension 2: 快乐/奖励
    ("庆祝", 2),
    ("奖励自己", 2),
    ("开心", 2),
    ("节日", 2),
    # Dimension 3: 无聊/习惯
    ("随手买的", 3),
    ("没事干", 3),
    ("习惯了", 3),
    ("打发时间", 3),
    # Dimension 4: 社交驱动
    ("聚餐", 4),
    ("随份子", 4),
    ("朋友带着买的", 4),
    ("请客", 4),
]


def seed_categories(session) -> int:
    """Insert preset categories if they don't already exist. Returns count of new rows."""
    created = 0

    for parent_name, pool_type, cat_type, sort_order, children in PRESET_CATEGORIES:
        # Check if parent already exists (system preset: user_id IS NULL)
        existing_parent = (
            session.query(Category)
            .filter(Category.name == parent_name, Category.user_id.is_(None), Category.parent_id.is_(None))
            .first()
        )
        if existing_parent is None:
            parent = Category(
                user_id=None,
                name=parent_name,
                icon=None,
                parent_id=None,
                pool_type=pool_type,
                type=cat_type,
                sort_order=sort_order,
                is_active=True,
            )
            session.add(parent)
            session.flush()  # get parent.id for children
            created += 1
        else:
            parent = existing_parent

        for child_name, child_pool, child_type, child_sort in children:
            existing_child = (
                session.query(Category)
                .filter(Category.name == child_name, Category.user_id.is_(None), Category.parent_id == parent.id)
                .first()
            )
            if existing_child is None:
                child = Category(
                    user_id=None,
                    name=child_name,
                    icon=None,
                    parent_id=parent.id,
                    pool_type=child_pool,
                    type=child_type,
                    sort_order=child_sort,
                    is_active=True,
                )
                session.add(child)
                created += 1

    session.commit()
    return created


def seed_emotion_tags(session) -> int:
    """Insert preset emotion tags if they don't already exist. Returns count of new rows."""
    created = 0

    for tag_name, dimension in PRESET_EMOTION_TAGS:
        existing = (
            session.query(EmotionTag)
            .filter(EmotionTag.name == tag_name)
            .first()
        )
        if existing is None:
            tag = EmotionTag(
                name=tag_name,
                dimension=dimension,
                is_system=True,
            )
            session.add(tag)
            created += 1

    session.commit()
    return created


def main():
    """Run all seed functions."""
    session = SessionLocal()
    try:
        print("Seeding categories...")
        cat_count = seed_categories(session)
        print(f"  → Created {cat_count} new categories.")

        print("Seeding emotion tags...")
        tag_count = seed_emotion_tags(session)
        print(f"  → Created {tag_count} new emotion tags.")

        print("Done! Seed data complete.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
