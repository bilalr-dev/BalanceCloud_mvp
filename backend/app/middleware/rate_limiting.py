"""
Redis-based Rate Limiting Middleware
"""

import time
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Redis-based rate limiting middleware
    
    Limits requests per minute per IP address using Redis.
    Falls back to in-memory storage if Redis is unavailable.
    """

    def __init__(self, app, requests_per_minute: int = None):
        super().__init__(app)
        self.requests_per_minute = (
            requests_per_minute or settings.RATE_LIMIT_REQUESTS_PER_MINUTE
        )
        self.redis_client = None
        self.memory_store = {}  # Fallback: {ip: [(timestamp, count), ...]}
        self._init_redis()

    def _init_redis(self):
        """Initialize Redis client"""
        if not settings.RATE_LIMIT_ENABLED:
            return

        try:
            import redis.asyncio as redis

            # Note: We'll create the connection in async context
            # Store the URL for later connection
            self.redis_url = settings.REDIS_URL
            self.redis_client = None  # Will be initialized on first use
        except Exception:
            # Redis not available, use in-memory fallback
            self.redis_client = None
            self.redis_url = None

    async def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded IP (from proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client IP
        if request.client:
            return request.client.host

        return "unknown"

    async def _init_redis_client(self):
        """Initialize Redis client if not already initialized"""
        if self.redis_client is not None:
            return

        if not hasattr(self, "redis_url") or not self.redis_url:
            return

        try:
            import redis.asyncio as redis

            self.redis_client = redis.from_url(
                self.redis_url, decode_responses=True
            )
        except Exception:
            # Redis not available, use in-memory fallback
            self.redis_client = None

    async def _check_rate_limit_redis(self, ip: str) -> tuple[bool, int, int]:
        """
        Check rate limit using Redis
        
        Returns:
            (is_allowed, remaining_requests, reset_time)
        """
        await self._init_redis_client()

        if not self.redis_client:
            return True, self.requests_per_minute, 60

        try:
            key = f"rate_limit:{ip}"
            current_time = int(time.time())
            window_start = current_time - 60  # 1 minute window

            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)  # Remove old entries
            pipe.zcard(key)  # Count current requests
            pipe.zadd(key, {str(current_time): current_time})  # Add current request
            pipe.expire(key, 60)  # Set expiration
            results = await pipe.execute()

            current_count = results[1] or 0
            is_allowed = current_count < self.requests_per_minute
            remaining = max(0, self.requests_per_minute - current_count - 1)
            reset_time = 60 - (current_time % 60)

            return is_allowed, remaining, reset_time
        except Exception:
            # Redis error, fallback to allowing request
            return True, self.requests_per_minute, 60

    async def _check_rate_limit_memory(self, ip: str) -> tuple[bool, int, int]:
        """
        Check rate limit using in-memory storage (fallback)
        
        Returns:
            (is_allowed, remaining_requests, reset_time)
        """
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window

        # Clean old entries
        if ip in self.memory_store:
            self.memory_store[ip] = [
                ts for ts in self.memory_store[ip] if ts > window_start
            ]
        else:
            self.memory_store[ip] = []

        # Check current count
        current_count = len(self.memory_store[ip])
        is_allowed = current_count < self.requests_per_minute

        # Add current request
        if is_allowed:
            self.memory_store[ip].append(current_time)

        remaining = max(0, self.requests_per_minute - current_count - 1)
        reset_time = int(60 - (current_time % 60))

        return is_allowed, remaining, reset_time

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process request with rate limiting"""
        # Skip rate limiting if disabled
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        # Skip rate limiting for health check endpoint
        if request.url.path in ["/api/health", "/"]:
            return await call_next(request)

        # Get client IP
        client_ip = await self._get_client_ip(request)

        # Check rate limit
        if self.redis_client:
            is_allowed, remaining, reset_time = await self._check_rate_limit_redis(
                client_ip
            )
        else:
            is_allowed, remaining, reset_time = await self._check_rate_limit_memory(
                client_ip
            )

        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)

        # Return 429 if rate limit exceeded
        if not is_allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded: {self.requests_per_minute} requests per minute",
                    "retry_after": reset_time,
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time),
                },
            )

        return response
