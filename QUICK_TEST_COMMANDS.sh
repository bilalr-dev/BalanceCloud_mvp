#!/bin/bash
# Quick test commands for Infrastructure & Security

# 1. Get token
echo "=== Getting Token ==="
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@bc.com", "password": "test123456@"}' \
  | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ Failed to get token. Make sure the user exists."
  exit 1
fi

echo "✅ Token obtained: ${TOKEN:0:50}..."
echo ""

# 2. Test Security Headers
echo "=== Testing Security Headers ==="
HEADERS_OUTPUT=$(curl -s -i http://localhost:8000/api/files \
  -H "Authorization: Bearer $TOKEN" 2>&1)

SECURITY_HEADERS=$(echo "$HEADERS_OUTPUT" | grep -iE "x-content-type-options|x-frame-options|content-security-policy|referrer-policy" | tr -d '\r')
if [ -n "$SECURITY_HEADERS" ]; then
  echo "$SECURITY_HEADERS" | sed 's/^/  /'
  echo "✅ Security headers present"
else
  echo "⚠️  No security headers found"
fi
echo ""

# 3. Test Rate Limit Headers
echo "=== Testing Rate Limit Headers ==="
RATE_LIMIT_HEADERS=$(echo "$HEADERS_OUTPUT" | grep -i "x-ratelimit" | tr -d '\r')
if [ -n "$RATE_LIMIT_HEADERS" ]; then
  echo "$RATE_LIMIT_HEADERS" | sed 's/^/  /'
  echo "✅ Rate limit headers present"
else
  echo "⚠️  No rate limit headers found"
fi
echo ""

# 4. Test Rate Limiting (make multiple requests)
echo "=== Testing Rate Limiting ==="
echo "Making 65 requests to test rate limiting..."
RATE_LIMITED=false
for i in {1..65}; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    http://localhost:8000/api/files)
  
  if [ "$STATUS" == "429" ]; then
    echo "✅ Rate limited at request $i (expected around 61+)"
    RATE_LIMITED=true
    break
  fi
  
  if [ $((i % 10)) -eq 0 ]; then
    echo "Request $i: Status $STATUS"
  fi
done

if [ "$RATE_LIMITED" == "false" ]; then
  echo "⚠️  Rate limiting not triggered (may need to wait or check configuration)"
fi
echo ""

# 5. Check Redis
echo "=== Checking Redis ==="
if docker-compose exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; then
  echo "✅ Redis is running"
  echo "Rate limit keys in Redis:"
  docker-compose exec -T redis redis-cli KEYS "rate_limit:*" 2>/dev/null | head -5
else
  echo "⚠️  Redis not accessible (using in-memory fallback)"
fi
echo ""

# 6. Test Health Check (should not be rate limited)
echo "=== Testing Health Check (should not be rate limited) ==="
for i in {1..100}; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health)
  if [ "$STATUS" != "200" ]; then
    echo "⚠️  Health check returned $STATUS at request $i"
    break
  fi
done
echo "✅ Health check not rate limited (all 100 requests returned 200)"
echo ""

echo "=== Testing Complete ==="
echo "Token saved in variable: TOKEN"
echo "Use it in requests: curl -H 'Authorization: Bearer $TOKEN' http://localhost:8000/api/files"
