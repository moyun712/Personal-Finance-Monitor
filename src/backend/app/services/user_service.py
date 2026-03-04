"""User business logic — registration, login, profile update."""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserProfileUpdateRequest, UserRegisterRequest
from app.utils.security import create_access_token, hash_password, verify_password


def register_user(db: Session, req: UserRegisterRequest) -> User:
    """Create a new user account.

    Raises:
        HTTPException 409 — username already taken.
    """
    existing = db.execute(select(User).where(User.username == req.username)).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已被注册",
        )

    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        nickname=req.nickname,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, username: str, password: str) -> str:
    """Authenticate and return a JWT access token.

    Raises:
        HTTPException 401 — invalid credentials.
    """
    user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    return create_access_token(user.id)


def update_profile(db: Session, user: User, req: UserProfileUpdateRequest) -> User:
    """Partially update user profile fields (nickname, monthly_income, payday).

    Only non-None fields in the request are applied.
    """
    update_data = req.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user
