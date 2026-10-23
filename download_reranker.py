"""Download only hash-verified files from one pinned public reranker revision."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

MODEL = "BAAI/bge-reranker-base"
REVISION = "2cfc18c9415c912f9d8155881c133215df768a70"
FILES = {
    "config.json": (799, "git", "ff248a5f7d76e27b10778b3c593c9fba1df4c448"),
    "model.safetensors": (1112206140, "sha256", "ced967c45fd1902eb92716c9ceeca7c95a936770ea9db611f5a841b926e33fbd"),
    "sentencepiece.bpe.model": (5069051, "sha256", "cfc8146abe2a0488e9e2a0c56de7952f7c11ab059eca145a0a727afce0db2865"),
    "special_tokens_map.json": (279, "git", "68171d1ff68b731a33d119708476692c094a466b"),
    "tokenizer.json": (17098107, "sha256", "9eb652ac4e40cc093272bbbe0f55d521cf67570060227109b5cdc20945a4489e"),
    "tokenizer_config.json": (443, "git", "059214673d9d6d2ee319411e2ffec8c024b816d5"),
}


def identity(path, size, kind):
    digest = hashlib.sha256() if kind == "sha256" else hashlib.sha1(b"blob " + str(size).encode() + b"\0")
    if not path.is_file() or path.stat().st_size != size:
        return None
    with path.open("rb") as f:
        for data in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(data)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    for name, (size, kind, expected) in FILES.items():
        target = args.output / name
        if identity(target, size, kind) != expected:
            temp = args.output / (name + ".partial")
            url = f"https://huggingface.co/{MODEL}/resolve/{REVISION}/{name}"
            digest = hashlib.sha256() if kind == "sha256" else hashlib.sha1(b"blob " + str(size).encode() + b"\0")
            total = 0
            with urllib.request.urlopen(url, timeout=60) as response, temp.open("wb") as f:
                for data in iter(lambda: response.read(1024 * 1024), b""):
                    total += len(data)
                    if total > size:
                        raise ValueError("Downloaded file exceeds pinned size")
                    digest.update(data)
                    f.write(data)
            if total != size or digest.hexdigest() != expected:
                raise ValueError("Downloaded file identity mismatch: " + name)
            temp.replace(target)
        record = {"name": name, "bytes": size, "identity_kind": kind, "identity": expected, "verified": True}
        records.append(record)
        print(json.dumps(record), flush=True)
    (args.output / "download-record.json").write_text(json.dumps({"model": MODEL, "revision": REVISION, "files": records}, indent=2) + "\n")


if __name__ == "__main__":
    main()
