"""Describe supplied source references without fetching or authenticating them."""
import re
from urllib.parse import urlsplit


def describe_source(url):
    parsed = urlsplit(url)
    match = re.fullmatch(r"/([^/]+)/([^/]+)/blob/([0-9a-fA-F]{40})/(.+)", parsed.path)
    pinned = bool(parsed.scheme == "https" and parsed.netloc == "github.com" and match
                  and not parsed.query and not any(part in (".", "..") for part in parsed.path.split("/")))
    return {
        "reference_type": "github_commit" if pinned else "immutable_reference_not_established",
        "commit": match[3].lower() if pinned else None,
        "remote_content_verified_this_review": False,
        "warning": ("Source link uses a full Git commit reference. This review checks supplied file hashes; it does not fetch the link or authenticate its contents."
                    if pinned else "The source link is not established as immutable. Its contents or line numbers can differ from the supplied guide. This review does not fetch or authenticate it."),
    }
