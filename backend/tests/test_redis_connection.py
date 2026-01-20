#!/usr/bin/env python3
"""
Test Redis connectivity
"""

import redis
from app.core.config import settings


def test_connection():
    """Test Redis connection"""
    print(f"Testing connection to: {settings.REDIS_URL}")
    print("-" * 60)

    try:
        r = redis.from_url(settings.REDIS_URL)

        # Test ping
        response = r.ping()
        if response:
            print("✅ Redis connection successful!")

            # Get Redis info
            info = r.info()
            print(f"✅ Redis version: {info.get('redis_version', 'unknown')}")
            print(f"✅ Connected clients: {info.get('connected_clients', 'unknown')}")
            print(f"✅ Used memory: {info.get('used_memory_human', 'unknown')}")

            # Test set/get
            r.set("test_key", "test_value", ex=10)
            value = r.get("test_key")
            if value == b"test_value":
                print("✅ Redis read/write test passed!")
                r.delete("test_key")

            print("-" * 60)
            print("✅ Redis connectivity test passed!")
            return True
        else:
            print("❌ Redis ping failed")
            return False

    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("-" * 60)
        print("Troubleshooting:")
        print("1. Make sure Redis is running: docker-compose up redis")
        print("2. Check REDIS_URL in config.py")
        print("3. Verify Redis is accessible")
        return False


if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1)
