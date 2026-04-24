from urllib.parse import urlparse, parse_qs


def extract_qs(url: str) -> str | None:
    parsed = urlparse(url)
    qs = parse_qs(parsed.query).get("qs")
    return qs[0] if qs else None