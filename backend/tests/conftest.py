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
    # Create a new session for each test
    # Ensure we're using a fresh connection from the pool
    # The pool_pre_ping setting will verify connections before using them
    async with AsyncSessionLocal() as session:
        try:
            # Force a connection to be established in the current event loop
            await session.connection()
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
    from sqlalchemy import select
    
    # Use unique email for each test run
    unique_email = f"test_{uuid4().hex[:8]}@example.com"
    
    user = User(
        id=uuid4(),
        email=unique_email,
        password_hash="hashed_password",  # In real tests, use proper hashing
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
