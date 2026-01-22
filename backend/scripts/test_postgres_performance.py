#!/usr/bin/env python3
"""
PostgreSQL Performance Testing Script

Tests database performance with various queries and operations.
"""

import asyncio
import time
from uuid import uuid4

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.db_optimization import db_optimizer
from app.models.file import File
from app.models.storage_chunk import StorageChunk
from app.models.user import User


async def test_query_performance(db: AsyncSession):
    """Test query performance"""
    print("\n" + "=" * 60)
    print("Query Performance Tests")
    print("=" * 60)

    # Test 1: User lookup by email
    print("\n1. User lookup by email:")
    start = time.time()
    result = await db.execute(select(User).where(User.email == "test@example.com"))
    user = result.scalar_one_or_none()
    elapsed = (time.time() - start) * 1000
    print(f"   Time: {elapsed:.2f}ms")
    print(f"   Result: {'Found' if user else 'Not found'}")

    # Test 2: File lookup by user_id and file_id
    if user:
        print("\n2. File lookup by user_id and file_id:")
        start = time.time()
        result = await db.execute(
            select(File).where(File.user_id == user.id).limit(1)
        )
        file = result.scalar_one_or_none()
        elapsed = (time.time() - start) * 1000
        print(f"   Time: {elapsed:.2f}ms")
        print(f"   Result: {'Found' if file else 'Not found'}")

        # Test 3: Chunks lookup by file_id
        if file:
            print("\n3. Chunks lookup by file_id:")
            start = time.time()
            result = await db.execute(
                select(StorageChunk)
                .where(StorageChunk.file_id == file.id)
                .order_by(StorageChunk.chunk_index)
            )
            chunks = result.scalars().all()
            elapsed = (time.time() - start) * 1000
            print(f"   Time: {elapsed:.2f}ms")
            print(f"   Chunks found: {len(chunks)}")

    # Test 4: List files by user_id and parent_id
    if user:
        print("\n4. List files by user_id and parent_id:")
        start = time.time()
        result = await db.execute(
            select(File).where(
                File.user_id == user.id, File.parent_id.is_(None)
            )
        )
        files = result.scalars().all()
        elapsed = (time.time() - start) * 1000
        print(f"   Time: {elapsed:.2f}ms")
        print(f"   Files found: {len(files)}")


async def test_index_usage(db: AsyncSession):
    """Test if indexes are being used"""
    print("\n" + "=" * 60)
    print("Index Usage Analysis")
    print("=" * 60)

    queries = [
        ("User by email", "SELECT * FROM users WHERE email = 'test@example.com';"),
        (
            "Files by user_id",
            "SELECT * FROM files WHERE user_id = '00000000-0000-0000-0000-000000000000' LIMIT 10;",
        ),
        (
            "Chunks by file_id",
            "SELECT * FROM storage_chunks WHERE file_id = '00000000-0000-0000-0000-000000000000' ORDER BY chunk_index;",
        ),
    ]

    for name, query in queries:
        print(f"\n{name}:")
        result = await db_optimizer.analyze_query(db, query)
        if result["status"] == "success":
            print(result["plan"])
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")


async def test_concurrent_queries(db_factory: async_sessionmaker):
    """Test concurrent query performance"""
    print("\n" + "=" * 60)
    print("Concurrent Query Performance")
    print("=" * 60)

    async def run_query(session_num: int):
        async with db_factory() as db:
            start = time.time()
            result = await db.execute(select(User).limit(10))
            users = result.scalars().all()
            elapsed = (time.time() - start) * 1000
            return elapsed, len(users)

    # Run 10 concurrent queries
    print("\nRunning 10 concurrent queries...")
    start = time.time()
    tasks = [run_query(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    total_time = (time.time() - start) * 1000

    avg_time = sum(r[0] for r in results) / len(results)
    print(f"   Total time: {total_time:.2f}ms")
    print(f"   Average query time: {avg_time:.2f}ms")
    print(f"   Queries completed: {len(results)}")


async def main():
    """Main test function"""
    print("PostgreSQL Performance Testing")
    print("=" * 60)

    # Create database connection
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        # Create indexes
        print("\nCreating database indexes...")
        results = await db_optimizer.create_indexes(async_session())
        for index_name, status in results.items():
            print(f"   {index_name}: {status}")

        # Run performance tests
        async with async_session() as db:
            await test_query_performance(db)
            await test_index_usage(db)

        # Test concurrent queries
        await test_concurrent_queries(async_session)

        # Get table statistics
        print("\n" + "=" * 60)
        print("Table Statistics")
        print("=" * 60)
        async with async_session() as db:
            for table in ["users", "files", "storage_chunks"]:
                print(f"\n{table}:")
                stats = await db_optimizer.get_table_stats(db, table)
                if stats["status"] == "success":
                    print(f"   Columns analyzed: {len(stats['stats'])}")
                else:
                    print(f"   Error: {stats.get('error', 'Unknown error')}")

        print("\n" + "=" * 60)
        print("Performance testing complete!")
        print("=" * 60)

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
