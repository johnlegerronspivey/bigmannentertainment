"""
Application middleware — performance tracking, security headers, rate limiting.
Extracted from server.py for modularity.
"""
import time
from fastapi import Request
from performance_monitor import perf_monitor
from rate_limiter import rate_limit_middleware as _rate_limit


async def performance_tracking_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    endpoint = f"{request.method} {request.url.path}"
    perf_monitor.record_request(endpoint, duration, response.status_code, request.method)
    response.headers['X-Response-Time'] = f"{duration:.3f}s"
    return response


async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(self), geolocation=()"
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    return response


async def apply_rate_limiting(request: Request, call_next):
    return await _rate_limit(request, call_next)
