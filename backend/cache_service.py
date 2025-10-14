"""
Simple in-memory caching service for API responses
Improves performance by caching frequently accessed data
"""
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import json
import hashlib


class CacheService:
    """In-memory cache with TTL support"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generate a cache key from prefix and parameters"""
        params_str = json.dumps(kwargs, sort_keys=True)
        key_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key not in self._cache:
            return None
            
        entry = self._cache[key]
        if datetime.utcnow() > entry['expires_at']:
            # Expired, remove from cache
            del self._cache[key]
            return None
            
        entry['hits'] += 1
        entry['last_accessed'] = datetime.utcnow()
        return entry['value']
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set value in cache with TTL (default 5 minutes)"""
        self._cache[key] = {
            'value': value,
            'expires_at': datetime.utcnow() + timedelta(seconds=ttl_seconds),
            'created_at': datetime.utcnow(),
            'last_accessed': datetime.utcnow(),
            'hits': 0
        }
    
    def delete(self, key: str):
        """Delete specific key from cache"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self):
        """Clear entire cache"""
        self._cache.clear()
    
    def cleanup_expired(self):
        """Remove all expired entries"""
        now = datetime.utcnow()
        expired_keys = [
            key for key, entry in self._cache.items()
            if now > entry['expires_at']
        ]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self._cache)
        total_hits = sum(entry['hits'] for entry in self._cache.values())
        
        expired_count = sum(
            1 for entry in self._cache.values()
            if datetime.utcnow() > entry['expires_at']
        )
        
        return {
            'total_entries': total_entries,
            'active_entries': total_entries - expired_count,
            'expired_entries': expired_count,
            'total_hits': total_hits,
            'average_hits': total_hits / total_entries if total_entries > 0 else 0
        }


# Global cache instance
cache = CacheService()


# Decorator for caching API responses
def cached_response(prefix: str, ttl_seconds: int = 300):
    """Decorator to cache function responses"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            cache_key = cache._generate_key(prefix, args=args, kwargs=kwargs)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            return result
        
        return wrapper
    return decorator
