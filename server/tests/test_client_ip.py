"""Unit tests for trusted proxy extraction and client IP resolution."""

from unittest.mock import MagicMock
import pytest
from fastapi import Request

from src.core.config import settings
from src.core.security import extract_client_ip


def make_mock_request(
    client_host: str | None = "127.0.0.1",
    headers: dict[str, str] | None = None,
) -> Request:
    """Build a mock FastAPI Request object."""
    req = MagicMock(spec=Request)
    if client_host is not None:
        client_mock = MagicMock()
        client_mock.host = client_host
        req.client = client_mock
    else:
        req.client = None

    header_dict = headers or {}
    req.headers = {k.lower(): v for k, v in header_dict.items()}
    return req


def test_direct_connection_untrusted():
    """Direct connection without trusted proxy returns immediate peer IP, ignoring spoofed headers."""
    settings.TRUSTED_PROXY_IPS = ["10.0.0.0/8"]
    settings.TRUST_CLOUDFLARE_PROXIES = False

    req = make_mock_request(
        client_host="203.0.113.195",
        headers={"X-Forwarded-For": "198.51.100.1, 10.0.0.1"},
    )
    ip = extract_client_ip(req)
    assert ip == "203.0.113.195"


def test_single_trusted_proxy():
    """Request through single trusted proxy extracts the client IP from X-Forwarded-For."""
    settings.TRUSTED_PROXY_IPS = ["10.0.0.1"]
    settings.TRUST_CLOUDFLARE_PROXIES = False

    req = make_mock_request(
        client_host="10.0.0.1",
        headers={"X-Forwarded-For": "203.0.113.195"},
    )
    ip = extract_client_ip(req)
    assert ip == "203.0.113.195"


def test_chained_trusted_proxies_traversal():
    """Right-to-left traversal hops over trusted intermediate proxies and stops at first untrusted IP."""
    settings.TRUSTED_PROXY_IPS = ["10.0.0.0/8", "172.16.0.0/12"]
    settings.TRUST_CLOUDFLARE_PROXIES = False

    # Immediate peer: 10.0.0.1 (trusted)
    # X-Forwarded-For: 198.51.100.25 (untrusted client), 172.16.5.1 (trusted proxy)
    req = make_mock_request(
        client_host="10.0.0.1",
        headers={"X-Forwarded-For": "198.51.100.25, 172.16.5.1"},
    )
    ip = extract_client_ip(req)
    assert ip == "198.51.100.25"


def test_chained_all_trusted_proxies():
    """If all hops in X-Forwarded-For are trusted proxies, returns the leftmost hop."""
    settings.TRUSTED_PROXY_IPS = ["10.0.0.0/8"]
    settings.TRUST_CLOUDFLARE_PROXIES = False

    req = make_mock_request(
        client_host="10.0.0.1",
        headers={"X-Forwarded-For": "10.0.0.5, 10.0.0.4"},
    )
    ip = extract_client_ip(req)
    assert ip == "10.0.0.5"


def test_cloudflare_trusted_proxy():
    """Cloudflare CF-Connecting-IP is respected when peer is within Cloudflare CIDR range."""
    settings.TRUST_CLOUDFLARE_PROXIES = True
    # 173.245.48.5 is within 173.245.48.0/20
    req = make_mock_request(
        client_host="173.245.48.5",
        headers={"CF-Connecting-IP": "203.0.113.42"},
    )
    ip = extract_client_ip(req)
    assert ip == "203.0.113.42"


def test_cloudflare_untrusted_peer_ignored():
    """CF-Connecting-IP is ignored when immediate peer is not a recognized Cloudflare proxy."""
    settings.TRUST_CLOUDFLARE_PROXIES = True
    settings.TRUSTED_PROXY_IPS = []

    req = make_mock_request(
        client_host="198.51.100.5",
        headers={"CF-Connecting-IP": "203.0.113.42"},
    )
    ip = extract_client_ip(req)
    assert ip == "198.51.100.5"


def test_malformed_headers_fallback():
    """Malformed or invalid IP values in headers safely fall back to immediate peer without error."""
    settings.TRUSTED_PROXY_IPS = ["10.0.0.1"]
    settings.TRUST_CLOUDFLARE_PROXIES = False

    req = make_mock_request(
        client_host="10.0.0.1",
        headers={"X-Forwarded-For": "invalid-ip-string, 10.0.0.1"},
    )
    ip = extract_client_ip(req)
    assert ip == "10.0.0.1"


def test_ipv6_handling():
    """Supports IPv6 client and proxy addresses correctly."""
    settings.TRUSTED_PROXY_IPS = ["2001:db8::/32"]
    settings.TRUST_CLOUDFLARE_PROXIES = False

    req = make_mock_request(
        client_host="2001:db8::1",
        headers={"X-Forwarded-For": "2607:f8b0:4005:805::200e"},
    )
    ip = extract_client_ip(req)
    assert ip == "2607:f8b0:4005:805::200e"


def test_missing_client_host():
    """Gracefully handles missing or None client host."""
    req = make_mock_request(client_host=None)
    ip = extract_client_ip(req)
    assert ip == "127.0.0.1"
