"""Pydantic schemas for user-related API requests and responses."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# ── Registration ──────────────────────────────────────────────


class UserRegisterRequest(BaseModel):
    """POST /api/v1/auth/register request body."""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    nickname: str | None = Field(None, max_length=50, description="昵称（可选）")


# ── Login ─────────────────────────────────────────────────────


class UserLoginRequest(BaseModel):
    """POST /api/v1/auth/login request body."""

    username: str = Field(..., min_length=1, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class TokenResponse(BaseModel):
    """Successful login response containing the JWT."""

    access_token: str
    token_type: str = "bearer"


# ── User info ─────────────────────────────────────────────────


class UserResponse(BaseModel):
    """Public user info (never includes password)."""

    id: int
    username: str
    nickname: str | None = None
    monthly_income: Decimal | None = None
    payday: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Profile update (Onboarding / Settings) ───────────────────


class UserProfileUpdateRequest(BaseModel):
    """PUT /api/v1/auth/profile request body (partial update)."""

    nickname: str | None = Field(None, max_length=50, description="昵称")
    monthly_income: Decimal | None = Field(None, ge=0, description="月收入")
    payday: int | None = Field(None, ge=1, le=31, description="发薪日 (1-31)")
