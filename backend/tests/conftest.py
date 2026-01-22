"""
Pytest fixtures for testing
"""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.database import Base, engine, AsyncSessionLocal
from app.models.user import User


@pytest.fixture(scope="function")
async def db_session():
    """Create a test database session"""
    # Use the same engine as the app
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture(scope="function")
async def test_user(db_session):
    """Create a test user"""
    user = User(
        id=uuid4(),
        email="test@example.com",
        password_hash="hashed_password",  # In real tests, use proper hashing
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
