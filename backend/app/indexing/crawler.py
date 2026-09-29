import hashlib
import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

def canonicalize(url: str) -> str:
    """
    Normalize URLs to a canonical form.
    Removes fragments and trailing slashes for consistent indexing.
    """
    if not url:
        return ""

    parsed = urlparse(url)
    # Remove fragments
    # Convert scheme and netloc to lowercase
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.lower() or "/"

    # Remove trailing slash from path
    if path.endswith('/') and path != '/':
        path = path.rstrip('/')
    ignored = {"ref", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id", "gclid", "fbclid"}
    query = urlencode(sorted((key, value) for key, value in parse_qsl(parsed.query, keep_blank_values=True) if key.lower() not in ignored))
    return urlunparse((scheme, netloc, path, parsed.params, query, ""))

def calculate_content_hash(content: str) -> str:
    """
    Calculate a SHA-256 hash of the document content to detect duplicates.
    """
    if not content or not content.strip():
        return ""
    normalized = re.sub(r"\s+", " ", content).strip().casefold()
    return "sha256:" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class SimpleCrawler:
    """Small URL/content utility facade retained for crawler integrations."""

    canonicalize = staticmethod(canonicalize)
    calculate_content_hash = staticmethod(calculate_content_hash)
