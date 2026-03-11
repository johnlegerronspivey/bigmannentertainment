"""
Rate limiting middleware for API endpoints
Prevents abuse and ensures fair usage
"""
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from typing import Dict, Tuple
from collections import defaultdict
import time


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Store: {ip: [(timestamp1, timestamp2, ...)]}
        self._minute_buckets: Dict[str, list] = defaultdict(list)
        self._hour_buckets: Dict[str, list] = defaultdict(list)
    
    def _cleanup_old_requests(self, bucket: list, time_window: timedelta):
        """Remove requests older than time window"""
        cutoff = datetime.utcnow() - time_window
        return [ts for ts in bucket if ts > cutoff]
    
    def check_rate_limit(self, identifier: str) -> Tuple[bool, Dict[str, any]]:
        """
        Check if request is within rate limits
        Returns: (is_allowed, info_dict)
        """
        now = datetime.utcnow()
        
        # Cleanup old requests
        self._minute_buckets[identifier] = self._cleanup_old_requests(
            self._minute_buckets[identifier], 
            timedelta(minutes=1)
        )
        self._hour_buckets[identifier] = self._cleanup_old_requests(
            self._hour_buckets[identifier], 
            timedelta(hours=1)
        )
        
        # Check minute limit
        minute_count = len(self._minute_buckets[identifier])
        if minute_count >= self.requests_per_minute:
            return False, {
                'limit_type': 'per_minute',
                'limit': self.requests_per_minute,
                'current': minute_count,
                'retry_after': 60
            }
        
        # Check hour limit
        hour_count = len(self._hour_buckets[identifier])
        if hour_count >= self.requests_per_hour:
            return False, {
                'limit_type': 'per_hour',
                'limit': self.requests_per_hour,
                'current': hour_count,
                'retry_after': 3600
            }
        
        # Add current request
        self._minute_buckets[identifier].append(now)
        self._hour_buckets[identifier].append(now)
        
        return True, {
            'minute_remaining': self.requests_per_minute - minute_count - 1,
            'hour_remaining': self.requests_per_hour - hour_count - 1
        }
    
    def get_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting (IP address or user ID)"""
        # Try to get user ID from token if authenticated
        if hasattr(request.state, 'user_id'):
            return f"user:{request.state.user_id}"
        
        # Fall back to IP address
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        client_host = request.client.host if request.client else 'unknown'
        return f"ip:{client_host}"


# Global rate limiter instance
rate_limiter = RateLimiter(
    requests_per_minute=100,  # 100 requests per minute
    requests_per_hour=2000     # 2000 requests per hour
)


# Middleware function for FastAPI
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    # Skip rate limiting for health checks
    if request.url.path.endswith('/health'):
        return await call_next(request)
    
    identifier = rate_limiter.get_identifier(request)
    is_allowed, info = rate_limiter.check_rate_limit(identifier)
    
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail={
                'error': 'Rate limit exceeded',
                'message': f'Too many requests. Limit: {info["limit"]} requests {info["limit_type"]}',
                'retry_after': info['retry_after'],
                **info
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    response.headers['X-RateLimit-Limit-Minute'] = str(rate_limiter.requests_per_minute)
    response.headers['X-RateLimit-Remaining-Minute'] = str(info.get('minute_remaining', 0))
    response.headers['X-RateLimit-Limit-Hour'] = str(rate_limiter.requests_per_hour)
    response.headers['X-RateLimit-Remaining-Hour'] = str(info.get('hour_remaining', 0))
    
    return response
