"""Fetch the single immutable source blob required by the packaged demo."""
import base64
import hashlib
import json
from pathlib import Path
import urllib.request

BLOB = "893527759a66e5293aded6999f8c6879b634c6d6"
COMMIT = "b39300d09d6d70297dc437015d4a49e484b7b77d"
SHA256 = "327a5710b6d529d1b24e1200d8eaf60bf50a478a0ecf541b227e92394091248d"


def main():
    target = Path(__file__).resolve().parent / "model-evaluation/sources/kong-guide.md"
    if target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest() != SHA256:
            raise ValueError("Existing demo source changed; move it before preparing the pinned source")
    else:
        with urllib.request.urlopen(f"https://api.github.com/repos/Kong/charts/contents/charts/kong/UPGRADE.md?ref={COMMIT}", timeout=30) as response:
            payload = json.loads(response.read(200_000))
        data = base64.b64decode(payload["content"])
        git_identity = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if payload.get("sha") != BLOB or git_identity != BLOB or hashlib.sha256(data).hexdigest() != SHA256:
            raise ValueError("Source identity mismatch")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print("Pinned Kong demo source bytes verified.")


if __name__ == "__main__":
    main()
