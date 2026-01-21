#!/usr/bin/env python3
"""
Test API endpoints
"""

import json
import os
import sys

import requests

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_register_user():
    """Test user registration"""
    print("\n🔍 Testing user registration...")
    try:
        data = {"email": "test@example.com", "password": "TestPassword123!"}
        response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
        if response.status_code == 201:
            print("✅ User registration passed!")
            result = response.json()
            print(f"   Access token received: {result.get('access_token', '')[:20]}...")
            return result.get("access_token")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return None


def test_login(email, password):
    """Test user login"""
    print("\n🔍 Testing user login...")
    try:
        data = {"email": email, "password": password}
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        if response.status_code == 200:
            print("✅ Login passed!")
            result = response.json()
            print(f"   Access token received: {result.get('access_token', '')[:20]}...")
            return result.get("access_token")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None


def test_get_current_user(token):
    """Test getting current user info"""
    print("\n🔍 Testing get current user...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        if response.status_code == 200:
            print("✅ Get current user passed!")
            user = response.json()
            print(f"   User email: {user.get('email')}")
            print(f"   User ID: {user.get('id')}")
            return True
        else:
            print(f"❌ Get current user failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get current user failed: {e}")
        return False


def test_list_files(token):
    """Test listing files"""
    print("\n🔍 Testing list files...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/files", headers=headers)
        if response.status_code == 200:
            print("✅ List files passed!")
            files = response.json()
            print(f"   Found {len(files.get('files', []))} file(s)")
            return True
        else:
            print(f"❌ List files failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ List files failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Testing Backend API Endpoints")
    print("=" * 60)

    # Test health check
    if not test_health_check():
        print("\n❌ Health check failed. Is the backend running?")
        print("   Start it with: uvicorn app.main:app --reload --port 8000")
        return

    # Test registration
    token = test_register_user()
    if not token:
        print("\n❌ Registration failed. Check backend logs.")
        return

    # Test login
    login_token = test_login("test@example.com", "TestPassword123!")
    if not login_token:
        print("\n❌ Login failed. Check backend logs.")
        return

    # Test get current user
    if not test_get_current_user(token):
        print("\n❌ Get current user failed.")
        return

    # Test list files
    if not test_list_files(token):
        print("\n❌ List files failed.")
        return

    print("\n" + "=" * 60)
    print("✅ All API tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
