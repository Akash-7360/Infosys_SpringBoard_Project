from fastapi import Request
from slowapi import Limiter
from app.core.config import settings


def get_client_ip(request: Request) -> str:
    """
    Extracts real client IP address for accurate rate limiting.
    Supports reverse proxies and CDNs (Render, Vercel, Cloudflare, AWS).
    """
    # X-Forwarded-For: client, proxy1, proxy2
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()

    # Cloudflare connecting IP
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()

    # Standard Real IP
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    # Direct client socket address fallback
    if request.client and request.client.host:
        return request.client.host

    return "127.0.0.1"


# Global singleton Limiter instance
limiter = Limiter(
    key_func=get_client_ip,
    default_limits=[settings.DEFAULT_RATE_LIMIT],
    enabled=settings.RATE_LIMIT_ENABLED,
    headers_enabled=False  # Handled cleanly via middleware without requiring Response in route parameters
)
