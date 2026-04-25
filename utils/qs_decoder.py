import base64
import urllib.parse


def decode_qs(qs: str):
    decoded = base64.b64decode(
        urllib.parse.unquote(qs)
    ).decode("utf-8")

    parts = decoded.split("|")

    return {
        "select1": parts[0],
        "spec_code": parts[1],
        "edu_form": parts[2],
        "edu_fin": parts[3],
    }