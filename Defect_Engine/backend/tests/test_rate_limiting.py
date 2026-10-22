"""
Unit tests for API Rate Limiting, Proxy IP Extraction, and HTTP 429 responses.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.limiter import limiter, get_client_ip


def test_rate_limit_headers_injected():
    """
    Verifies that rate limit headers (X-RateLimit-Limit, X-RateLimit-Remaining)
    are injected into successful API responses.
    """
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert "x-ratelimit-limit" in response.headers or "X-RateLimit-Limit" in response.headers
        assert "x-ratelimit-remaining" in response.headers or "X-RateLimit-Remaining" in response.headers


def test_rate_limit_exceeded_returns_429():
    """
    Verifies that exceeding the rate limit returns HTTP 429 Too Many Requests
    with standard error JSON and Retry-After header.
    """
    with TestClient(app) as client:
        # Use a distinct dummy IP to isolate test state
        headers = {"X-Forwarded-For": "198.51.100.42"}
        
        # Call /health until rate limit is exhausted (limit is 120/minute in main.py)
        # We can test against a specifically limited temporary route or test client IP isolation
        hit_429 = False
        for i in range(125):
            res = client.get("/health", headers=headers)
            if res.status_code == 429:
                hit_429 = True
                data = res.json()
                assert data["error"] == "Rate limit exceeded"
                assert "retry_after_seconds" in data
                assert "Retry-After" in res.headers or "retry-after" in res.headers
                break
        
        assert hit_429, "Expected HTTP 429 after exceeding route rate limit"


def test_client_ip_proxy_extraction():
    """
    Verifies that reverse proxy headers (X-Forwarded-For, CF-Connecting-IP, X-Real-IP)
    correctly isolate different client rate limit buckets.
    """
    from fastapi import Request

    # 1. Test X-Forwarded-For with comma separated proxies
    scope_forwarded = {
        "type": "http",
        "headers": [(b"x-forwarded-for", b"203.0.113.195, 70.41.3.18, 150.172.238.178")]
    }
    req_forwarded = Request(scope_forwarded)
    assert get_client_ip(req_forwarded) == "203.0.113.195"

    # 2. Test CF-Connecting-IP (Cloudflare)
    scope_cf = {
        "type": "http",
        "headers": [(b"cf-connecting-ip", b"198.51.100.99")]
    }
    req_cf = Request(scope_cf)
    assert get_client_ip(req_cf) == "198.51.100.99"

    # 3. Test X-Real-IP
    scope_real = {
        "type": "http",
        "headers": [(b"x-real-ip", b"192.0.2.1")]
    }
    req_real = Request(scope_real)
    assert get_client_ip(req_real) == "192.0.2.1"


def test_separate_client_ips_have_independent_quotas():
    """
    Verifies that client A hitting the rate limit does not block client B.
    """
    with TestClient(app) as client:
        ip_blocked = "198.51.100.11"
        ip_fresh = "198.51.100.22"

        # Exhaust quota for client A
        for _ in range(125):
            res = client.get("/health", headers={"X-Forwarded-For": ip_blocked})
            if res.status_code == 429:
                break

        # Client A should now be throttled
        res_blocked = client.get("/health", headers={"X-Forwarded-For": ip_blocked})
        assert res_blocked.status_code == 429

        # Client B with a different IP should NOT be throttled
        res_fresh = client.get("/health", headers={"X-Forwarded-For": ip_fresh})
        assert res_fresh.status_code == 200


if __name__ == "__main__":
    print("Running Rate Limiting & Proxy IP Tests...")
    test_rate_limit_headers_injected()
    print("✓ test_rate_limit_headers_injected PASSED")
    test_client_ip_proxy_extraction()
    print("✓ test_client_ip_proxy_extraction PASSED")
    test_rate_limit_exceeded_returns_429()
    print("✓ test_rate_limit_exceeded_returns_429 PASSED")
    test_separate_client_ips_have_independent_quotas()
    print("✓ test_separate_client_ips_have_independent_quotas PASSED")
    print("All Rate Limiting Tests Passed Successfully!")
