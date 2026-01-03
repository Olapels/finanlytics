import pytest
from datetime import timedelta
from fastapi import HTTPException

from backend.services.user_service import user_service, User


def test_hash_and_verify_password_round_trip():
    password = "S3cureP@ss!"
    hashed = user_service.hash_password(password)

    assert hashed != password
    assert user_service.verify_password(password, hashed) == True
    assert user_service.verify_password("wrong", hashed) == False


def test_create_and_decode_token_contains_subject_and_exp():
    token = user_service.create_access_token("user-123", expires_delta=timedelta(minutes=5))
    decoded = user_service.decode_token(token)

    assert decoded["sub"] == "user-123"
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_get_current_user_returns_user(monkeypatch):
    fake_user = User(
        user_id="user-123",
        email="demo@example.com",
        password="hashed",
        first_name="Demo",
        last_name="User",
        create_date=None,
    )
    token = user_service.create_access_token(fake_user.user_id, expires_delta=timedelta(minutes=5))

    async def fake_get_user_by_id(db, user_id):
        return fake_user

    monkeypatch.setattr(user_service, "get_user_by_id", fake_get_user_by_id)

    user = await user_service.get_current_user(token=token, db=None)

    assert user is fake_user


@pytest.mark.asyncio
async def test_get_current_user_raises_on_invalid_token(monkeypatch):
    async def fake_get_user_by_id(db, user_id):
        return None

    monkeypatch.setattr(user_service, "get_user_by_id", fake_get_user_by_id)

    with pytest.raises(HTTPException) as excinfo:
        await user_service.get_current_user(token="invalid.token.value", db=None)

    assert excinfo.value.status_code == 401
