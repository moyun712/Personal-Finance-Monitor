"""Tests for Phase 2 — User Authentication (Steps 2.1–2.7).

Covers:
  Step 2.1  — Password hashing (bcrypt)
  Step 2.2  — JWT token creation & decoding
  Step 2.3  — User registration API
  Step 2.4  — User login API
  Step 2.5  — JWT auth middleware / dependency
  Step 2.7  — Profile update API (onboarding)

Run with:  cd src/backend && python -m pytest tests/test_phase2.py -v
"""

import os
from datetime import datetime, timedelta, timezone

import jwt as pyjwt
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Disable proxy for httpx
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)

from app.config import settings
from app.database import SessionLocal
from app.main import app
from app.models.user import User
from app.utils.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

# Unique prefix for test data isolation
_PREFIX = "test_p2_"


# ── Fixtures ──────────────────────────────────────────────────


@pytest.fixture(scope="module")
def db():
    """Provide a DB session for the module; clean up test users afterward."""
    session = SessionLocal()
    yield session
    # Cleanup: delete test users
    session.execute(
        User.__table__.delete().where(User.username.like(f"{_PREFIX}%"))
    )
    session.commit()
    session.close()


@pytest_asyncio.fixture(scope="module")
async def client():
    """Async test client using ASGITransport (no network; in-process)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver", trust_env=False) as c:
        yield c


# ═══════════════════════════════════════════════════════════════
# Step 2.1 — Password Hashing
# ═══════════════════════════════════════════════════════════════


class TestPasswordHashing:
    """Step 2.1: bcrypt hashing utilities."""

    def test_hash_returns_bcrypt_format(self):
        h = hash_password("abc123")
        assert h.startswith("$2b$")

    def test_hash_different_each_time(self):
        h1 = hash_password("abc123")
        h2 = hash_password("abc123")
        assert h1 != h2, "Each hash should have a unique salt"

    def test_verify_correct_password(self):
        h = hash_password("abc123")
        assert verify_password("abc123", h) is True

    def test_verify_wrong_password(self):
        h = hash_password("abc123")
        assert verify_password("wrong", h) is False

    def test_verify_empty_password(self):
        h = hash_password("abc123")
        assert verify_password("", h) is False


# ═══════════════════════════════════════════════════════════════
# Step 2.2 — JWT Token
# ═══════════════════════════════════════════════════════════════


class TestJWTToken:
    """Step 2.2: JWT creation and decoding."""

    def test_create_and_decode(self):
        token = create_access_token(42)
        payload = decode_access_token(token)
        assert payload["sub"] == "42"
        assert "exp" in payload
        assert "iat" in payload

    def test_wrong_secret_fails(self):
        token = create_access_token(1)
        with pytest.raises(pyjwt.InvalidSignatureError):
            pyjwt.decode(token, "wrong-secret", algorithms=["HS256"])

    def test_expired_token_fails(self):
        """Manually craft an expired token."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "1",
            "exp": now - timedelta(seconds=10),
            "iat": now - timedelta(seconds=60),
        }
        token = pyjwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        with pytest.raises(pyjwt.ExpiredSignatureError):
            decode_access_token(token)

    def test_tampered_token_fails(self):
        token = create_access_token(1)
        # Replace the signature with a completely different string
        parts = token.split(".")
        tampered = f"{parts[0]}.{parts[1]}.INVALID_SIGNATURE_XXXXX"
        with pytest.raises(pyjwt.InvalidTokenError):
            decode_access_token(tampered)


# ═══════════════════════════════════════════════════════════════
# Step 2.3 — User Registration API
# ═══════════════════════════════════════════════════════════════


@pytest.mark.asyncio
class TestRegistration:
    """Step 2.3: POST /api/v1/auth/register."""

    async def test_register_success(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"username": f"{_PREFIX}alice", "password": "pass1234"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["username"] == f"{_PREFIX}alice"
        assert "id" in body
        assert "password" not in body
        assert "password_hash" not in body

    async def test_register_with_nickname(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"username": f"{_PREFIX}bob", "password": "pass1234", "nickname": "鲍勃"},
        )
        assert resp.status_code == 201
        assert resp.json()["nickname"] == "鲍勃"

    async def test_register_duplicate_username(self, client: AsyncClient):
        # First registration
        await client.post(
            "/api/v1/auth/register",
            json={"username": f"{_PREFIX}dup", "password": "pass1234"},
        )
        # Duplicate
        resp = await client.post(
            "/api/v1/auth/register",
            json={"username": f"{_PREFIX}dup", "password": "other123"},
        )
        assert resp.status_code == 409

    async def test_register_short_username(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"username": "ab", "password": "pass1234"},
        )
        assert resp.status_code == 422

    async def test_register_short_password(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"username": f"{_PREFIX}short", "password": "12345"},
        )
        assert resp.status_code == 422

    async def test_register_empty_username(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"username": "", "password": "pass1234"},
        )
        assert resp.status_code == 422

    async def test_password_stored_as_bcrypt(self, client: AsyncClient, db):
        """Verify the database stores bcrypt hash, not plaintext."""
        username = f"{_PREFIX}hashcheck"
        await client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": "mysecret"},
        )
        from sqlalchemy import select

        user = db.execute(select(User).where(User.username == username)).scalar_one()
        assert user.password_hash.startswith("$2b$")
        assert user.password_hash != "mysecret"


# ═══════════════════════════════════════════════════════════════
# Step 2.4 — User Login API
# ═══════════════════════════════════════════════════════════════


@pytest.mark.asyncio
class TestLogin:
    """Step 2.4: POST /api/v1/auth/login."""

    async def test_login_success(self, client: AsyncClient):
        # Ensure user exists
        await client.post(
            "/api/v1/auth/register",
            json={"username": f"{_PREFIX}loginuser", "password": "pass1234"},
        )
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": f"{_PREFIX}loginuser", "password": "pass1234"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    async def test_login_token_has_correct_sub(self, client: AsyncClient, db):
        # Register
        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={"username": f"{_PREFIX}subcheck", "password": "pass1234"},
        )
        user_id = reg_resp.json()["id"]
        # Login
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": f"{_PREFIX}subcheck", "password": "pass1234"},
        )
        token = login_resp.json()["access_token"]
        payload = decode_access_token(token)
        assert payload["sub"] == str(user_id)

    async def test_login_wrong_username(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent_user_xyz", "password": "pass1234"},
        )
        assert resp.status_code == 401

    async def test_login_wrong_password(self, client: AsyncClient):
        await client.post(
            "/api/v1/auth/register",
            json={"username": f"{_PREFIX}wrongpw", "password": "correct123"},
        )
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": f"{_PREFIX}wrongpw", "password": "wrong999"},
        )
        assert resp.status_code == 401

    async def test_login_error_message_hides_detail(self, client: AsyncClient):
        """Error message should be generic to avoid leaking account existence."""
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent_user_xyz", "password": "any"},
        )
        assert "用户名或密码错误" in resp.json()["detail"]


# ═══════════════════════════════════════════════════════════════
# Step 2.5 — JWT Auth Dependency (GET /api/v1/auth/me)
# ═══════════════════════════════════════════════════════════════


@pytest.mark.asyncio
class TestAuthMiddleware:
    """Step 2.5: JWT auth dependency tested through /me endpoint."""

    async def _get_token(self, client: AsyncClient, suffix: str = "meuser") -> str:
        username = f"{_PREFIX}{suffix}"
        await client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": "pass1234"},
        )
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": "pass1234"},
        )
        return resp.json()["access_token"]

    async def test_me_with_valid_token(self, client: AsyncClient):
        token = await self._get_token(client, "mevalid")
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["username"] == f"{_PREFIX}mevalid"
        assert "password" not in body
        assert "password_hash" not in body

    async def test_me_without_token(self, client: AsyncClient):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    async def test_me_with_expired_token(self, client: AsyncClient):
        """Craft an expired token and make sure it's rejected."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "1",
            "exp": now - timedelta(seconds=10),
            "iat": now - timedelta(seconds=60),
        }
        expired_token = pyjwt.encode(
            payload, settings.JWT_SECRET_KEY, algorithm="HS256"
        )
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert resp.status_code == 401

    async def test_me_with_tampered_token(self, client: AsyncClient):
        token = await self._get_token(client, "metamper")
        # Replace signature with a wrong one
        parts = token.split(".")
        tampered = f"{parts[0]}.{parts[1]}.INVALID_SIGNATURE_XXXXX"
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tampered}"},
        )
        assert resp.status_code == 401

    async def test_me_with_invalid_user_id(self, client: AsyncClient):
        """Token with sub pointing to non-existent user."""
        token = create_access_token(999999999)
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════
# Step 2.7 — Profile Update API (Onboarding)
# ═══════════════════════════════════════════════════════════════


@pytest.mark.asyncio
class TestProfileUpdate:
    """Step 2.7: PUT /api/v1/auth/profile."""

    async def _register_and_login(self, client: AsyncClient, suffix: str) -> str:
        username = f"{_PREFIX}{suffix}"
        await client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": "pass1234"},
        )
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": "pass1234"},
        )
        return resp.json()["access_token"]

    async def test_update_all_fields(self, client: AsyncClient):
        token = await self._register_and_login(client, "profile1")
        resp = await client.put(
            "/api/v1/auth/profile",
            json={"nickname": "小天", "monthly_income": 8000, "payday": 15},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["nickname"] == "小天"
        assert float(body["monthly_income"]) == 8000.0
        assert body["payday"] == 15

    async def test_update_partial(self, client: AsyncClient):
        token = await self._register_and_login(client, "profile2")
        resp = await client.put(
            "/api/v1/auth/profile",
            json={"payday": 25},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["payday"] == 25
        # Other fields should remain as default
        assert resp.json()["monthly_income"] is None

    async def test_update_without_token(self, client: AsyncClient):
        resp = await client.put(
            "/api/v1/auth/profile",
            json={"nickname": "test"},
        )
        assert resp.status_code == 401

    async def test_skip_onboarding(self, client: AsyncClient):
        """User skips onboarding — fields stay NULL."""
        token = await self._register_and_login(client, "profile3")
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["monthly_income"] is None
        assert resp.json()["payday"] is None

    async def test_update_income_then_verify(self, client: AsyncClient, db):
        """Verify profile update persists to database."""
        token = await self._register_and_login(client, "profile4")
        await client.put(
            "/api/v1/auth/profile",
            json={"monthly_income": 12000, "payday": 1},
            headers={"Authorization": f"Bearer {token}"},
        )
        from sqlalchemy import select

        user = db.execute(
            select(User).where(User.username == f"{_PREFIX}profile4")
        ).scalar_one()
        from decimal import Decimal

        assert user.monthly_income == Decimal("12000.00")
        assert user.payday == 1

    async def test_invalid_payday(self, client: AsyncClient):
        token = await self._register_and_login(client, "profile5")
        resp = await client.put(
            "/api/v1/auth/profile",
            json={"payday": 32},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422

    async def test_negative_income(self, client: AsyncClient):
        token = await self._register_and_login(client, "profile6")
        resp = await client.put(
            "/api/v1/auth/profile",
            json={"monthly_income": -100},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422
