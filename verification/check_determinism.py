"""Run the existing case-file CLI repeatedly; remove timing fields only."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VOLATILE_KEYS = frozenset({"inference_seconds", "processing_seconds", "elapsed_seconds",
                           "timestamp", "checked_at", "created_at", "generated_at"})


def normalize(value):
    if isinstance(value, dict):
        return {key: normalize(item) for key, item in value.items() if key not in VOLATILE_KEYS}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return value


def canonical_bytes(report):
    return json.dumps(normalize(report), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--expected-hash")
    args = parser.parse_args()
    if not 1 <= args.runs <= 10:
        parser.error("runs must be between one and ten")
    out = args.output_directory.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out / "result.json").exists():
        parser.error("Preserve the previous run; choose a new output directory")
    env = dict(os.environ)
    env.update(RERANKER_CPU_THREADS="1", TOKENIZERS_PARALLELISM="false", OMP_NUM_THREADS="1")
    command = [sys.executable, "upgrade_brief.py", "brief-cases/kong-readiness.json", "--root", ".",
               "--model-dir", str(args.model_dir.resolve()), "--format", "json"]
    records = []
    for number in range(1, args.runs + 1):
        run = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=180)
        prefix = out / f"run-{number:02}"
        prefix.with_suffix(".stdout.json").write_bytes(run.stdout)
        prefix.with_suffix(".stderr.txt").write_bytes(run.stderr)
        record = {"run": number, "command": command, "exit_code": run.returncode}
        if run.returncode == 0:
            report = json.loads(run.stdout)
            if report.get("model_calls", 0) < 1:
                raise RuntimeError("Actual model execution required")
            normalized = canonical_bytes(report)
            prefix.with_suffix(".normalized.json").write_bytes(normalized)
            record["normalized_sha256"] = hashlib.sha256(normalized).hexdigest()
        records.append(record)
        print(json.dumps(record), flush=True)
        if run.returncode:
            break
    hashes = {item.get("normalized_sha256") for item in records}
    identical = len(records) == args.runs and len(hashes) == 1 and None not in hashes
    comparison = None if not args.expected_hash else identical and hashes == {args.expected_hash}
    result = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "runs": records,
              "removed_keys_only": sorted(VOLATILE_KEYS), "python": sys.version,
              "machine": platform.machine(), "platform": platform.platform(),
              "environment_settings": {key: env[key] for key in ("RERANKER_CPU_THREADS", "TOKENIZERS_PARALLELISM", "OMP_NUM_THREADS")},
              "all_hashes_match": identical, "expected_hash": args.expected_hash,
              "expected_hash_match": comparison,
              "scope": "Only these executions of the fixed Kong input on the recorded environment; no guarantee for other inputs or hardware."}
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if identical and comparison is not False else 1


if __name__ == "__main__":
    raise SystemExit(main())
