from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'fitbuddy.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(120))
    age: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Float)
    goal: Mapped[str] = mapped_column(String(80))
    intensity: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(80), index=True)
    original_plan: Mapped[str] = mapped_column(Text)
    updated_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    nutrition_tip: Mapped[str] = mapped_column(Text)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def save_user(
    db: Session,
    *,
    user_id: str,
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> User:
    existing = db.scalar(select(User).where(User.user_id == user_id))
    if existing:
        existing.username = username
        existing.age = age
        existing.weight = weight
        existing.goal = goal
        existing.intensity = intensity
        db.commit()
        db.refresh(existing)
        return existing

    user = User(
        user_id=user_id,
        username=username,
        age=age,
        weight=weight,
        goal=goal,
        intensity=intensity,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def save_plan(
    db: Session,
    *,
    user_id: str,
    original_plan: str,
    nutrition_tip: str,
) -> Plan:
    plan = Plan(
        user_id=user_id,
        original_plan=original_plan,
        nutrition_tip=nutrition_tip,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_user(db: Session, user_id: str) -> Optional[User]:
    return db.scalar(select(User).where(User.user_id == user_id))


def get_plan(db: Session, user_id: str) -> Optional[Plan]:
    return db.scalar(
        select(Plan)
        .where(Plan.user_id == user_id)
        .order_by(Plan.created_at.desc())
    )


def get_original_plan(db: Session, user_id: str) -> Optional[str]:
    plan = get_plan(db, user_id)
    return plan.original_plan if plan else None


def update_plan(
    db: Session,
    *,
    user_id: str,
    updated_plan: str,
    feedback: str,
    nutrition_tip: Optional[str] = None,
) -> Optional[Plan]:
    plan = get_plan(db, user_id)
    if not plan:
        return None

    plan.updated_plan = updated_plan
    plan.feedback = feedback
    if nutrition_tip:
        plan.nutrition_tip = nutrition_tip
    db.commit()
    db.refresh(plan)
    return plan


def get_all_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at.desc())).all())


def get_all_plans(db: Session) -> list[Plan]:
    return list(db.scalars(select(Plan).order_by(Plan.created_at.desc())).all())


def get_user_plan_map(db: Session) -> dict[str, Plan]:
    plans = get_all_plans(db)
    result: dict[str, Plan] = {}
    for plan in plans:
        result.setdefault(plan.user_id, plan)
    return result


def delete_user(db: Session, user_id: str) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False

    plans = list(db.scalars(select(Plan).where(Plan.user_id == user_id)).all())
    for plan in plans:
        db.delete(plan)
    db.delete(user)
    db.commit()
    return True
