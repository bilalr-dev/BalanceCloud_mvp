#!/usr/bin/env python3
"""
Test database migrations
"""

import asyncio

from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine


async def test_migrations():
    """Test that all tables exist after migrations"""
    print("Testing database migrations...")
    print("-" * 60)

    try:
        async with engine.begin() as conn:
            # Get all tables
            result = await conn.execute(
                text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
            )
            tables = [row[0] for row in result.fetchall()]

            print(f"✅ Found {len(tables)} table(s):")
            for table in tables:
                print(f"   - {table}")

            # Expected tables
            expected_tables = {
                "users",
                "files",
                "cloud_accounts",
                "encryption_keys",
                "storage_chunks",
            }

            missing_tables = expected_tables - set(tables)
            if missing_tables:
                print(f"\n❌ Missing tables: {', '.join(missing_tables)}")
                return False

            # Check indexes
            print("\n📊 Checking indexes...")
            for table in expected_tables:
                result = await conn.execute(
                    text("""
                        SELECT indexname 
                        FROM pg_indexes 
                        WHERE tablename = :table_name
                        ORDER BY indexname
                    """),
                    {"table_name": table},
                )
                indexes = [row[0] for row in result.fetchall()]
                if indexes:
                    print(f"   {table}: {len(indexes)} index(es)")
                else:
                    print(f"   {table}: no indexes")

            # Check foreign keys
            print("\n🔗 Checking foreign keys...")
            result = await conn.execute(
                text("""
                    SELECT
                        tc.table_name,
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                    ORDER BY tc.table_name, kcu.column_name
                """)
            )
            foreign_keys = result.fetchall()
            if foreign_keys:
                print(f"   Found {len(foreign_keys)} foreign key(s):")
                for fk in foreign_keys:
                    print(f"   - {fk[0]}.{fk[1]} -> {fk[2]}.{fk[3]}")

            print("-" * 60)
            print("✅ All migrations verified successfully!")
            return True

    except Exception as e:
        print(f"❌ Migration test failed: {e}")
        print("-" * 60)
        return False


if __name__ == "__main__":
    success = asyncio.run(test_migrations())
    exit(0 if success else 1)
