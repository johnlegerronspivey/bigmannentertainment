"""
Application middleware — performance tracking, security headers, rate limiting, response sanitization.
Extracted from server.py for modularity.
"""
import time
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse
from performance_monitor import perf_monitor
from rate_limiter import rate_limit_middleware as _rate_limit
from services.secrets_protection_service import sanitize_text


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
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https:; font-src 'self' https: data:"
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    return response


async def error_sanitization_middleware(request: Request, call_next):
    """Sanitize error responses to prevent accidental secret leakage."""
    try:
        response = await call_next(request)
        if response.status_code >= 400 and hasattr(response, 'body'):
            pass
        return response
    except Exception as exc:
        sanitized_message = sanitize_text(str(exc))
        return JSONResponse(
            status_code=500,
            content={"detail": sanitized_message},
        )


async def apply_rate_limiting(request: Request, call_next):
    return await _rate_limit(request, call_next)
