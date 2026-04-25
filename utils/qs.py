from urllib.parse import parse_qs, urlparse


def extract_qs(value: str) -> str | None:
    """
    Extracts qs from a URL like:
    https://.../?qs=BASE64

    Also accepts a raw qs string and returns it unchanged.
    """
    value = value.strip()

    if "://" not in value and value and " " not in value:
        return value

    parsed = urlparse(value)
    qs_values = parse_qs(parsed.query).get("qs")
    if qs_values:
        return qs_values[0]

    return None
