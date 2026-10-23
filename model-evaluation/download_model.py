"""Download only allowlisted data files from a pinned public model revision."""
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
lock = json.loads((ROOT / "model-download-lock.json").read_text())
allowed = {"config.json", "generation_config.json", "model.safetensors", "tokenizer.json",
           "tokenizer_config.json", "vocab.json", "merges.txt", "LICENSE"}
dest = ROOT / "weights"
dest.mkdir(exist_ok=True)
records = []
for record in lock["files"]:
    name = record["rfilename"]
    if name not in allowed:
        continue
    path = dest / name
    digest = hashlib.sha256()
    size = 0
    if not path.exists():
        url = f"https://huggingface.co/{lock['model']}/resolve/{lock['revision']}/{name}"
        temp = dest / (name + ".partial")
        with urllib.request.urlopen(url, timeout=30) as response, temp.open("wb") as out:
            while data := response.read(4 * 1024 * 1024):
                out.write(data)
                digest.update(data)
                size += len(data)
                if size > 1_600_000_000:
                    raise RuntimeError("Model file exceeds the experiment limit")
        expected = record.get("lfs", {}).get("sha256")
        if expected and digest.hexdigest() != expected:
            raise RuntimeError("Model weight checksum mismatch")
        temp.rename(path)
    else:
        with path.open("rb") as source:
            while data := source.read(4 * 1024 * 1024):
                digest.update(data)
                size += len(data)
        expected = record.get("lfs", {}).get("sha256")
        if expected and digest.hexdigest() != expected:
            raise RuntimeError("Existing model weight checksum mismatch")
    records.append({"path": name, "sha256": digest.hexdigest(), "bytes": size})
    print("Verified", name, size, flush=True)
(ROOT / "download-result.json").write_text(json.dumps({"model":lock["model"],"revision":lock["revision"],"files":records},indent=2)+'\n')
