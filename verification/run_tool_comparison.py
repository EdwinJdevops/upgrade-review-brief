"""Bounded offline comparison; requires the separately pinned ShiftScope checkout."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shiftscope", required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    checkout = args.shiftscope.resolve()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=checkout, text=True).strip()
    expected_commit = "b67c4a8694749418f42385b2aa1b36ef1e4c48a0"
    if commit != expected_commit:
        raise ValueError("unexpected ShiftScope commit")
    # Refuse tracked modifications; untracked files are never imported deliberately.
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", "src/shiftscope"], cwd=checkout, check=True, capture_output=True)
    sys.path.insert(0, str(checkout / "src"))
    from shiftscope.analyzers.helm4.analyzer import Helm4ReadinessAnalyzer

    cases = [
        ("2.25.0", "kong-old-proxy-only", "16c38cfb76ffc4d103c7a1becb5b358ef0970eecfb75ac2a0fea74fe0e40fdf5"),
        ("2.26.0", "kong-new-proxy-only", "c28136139149b21ea1e7ef82bd64d8b8021b221ecc4a8668a7e447631c9a1203"),
    ]
    result = {
        "scope": "Offline chart lint and Helm 4 readiness only; not application runtime or full upgrade validation",
        "shiftscope_commit": commit,
        "python": sys.version,
        "dependencies": {n: importlib.metadata.version(n) for n in ("pydantic", "PyYAML")},
        "cases": [],
    }
    helm = root / "experiment/tools/helm"
    if hashlib.sha256(helm.read_bytes()).hexdigest() != "31895cbbc131017b16aa67d6a61ec6df474527a73d61f5a7be72d2d038b38c1d":
        raise ValueError("unexpected Helm binary")
    with tempfile.TemporaryDirectory(prefix="bounded-chart-comparison-") as tmp:
        temp = Path(tmp)
        for version, case, digest in cases:
            archive = root / f"experiment/inputs/kong-{version}.tgz"
            if hashlib.sha256(archive.read_bytes()).hexdigest() != digest:
                raise ValueError("unexpected chart archive")
            dest = temp / version
            dest.mkdir()
            with tarfile.open(archive, "r:gz") as chart:
                members = chart.getmembers()
                if len(members) > 2000 or sum(m.size for m in members) > 30_000_000:
                    raise ValueError("oversized chart")
                for m in members:
                    p = PurePosixPath(m.name)
                    if p.is_absolute() or ".." in p.parts or not (m.isfile() or m.isdir()):
                        raise ValueError("unsupported archive member")
                chart.extractall(dest, members=members, filter="data")
            values = root / f"experiment/inputs/{case}.yaml"
            command = [str(helm), "lint", str(dest / "kong"), "--strict", "--values", str(values), "--kubeconfig", "/dev/null"]
            completed = subprocess.run(command, text=True, capture_output=True, timeout=60, env={**os.environ, "KUBECONFIG": "/dev/null"})
            report = Helm4ReadinessAnalyzer().analyze(str(dest / "kong")).model_dump(mode="json")
            report["source"] = f"kong-{version}.tgz/kong"
            normalized_command = [part.replace(str(dest), "<extracted-chart>").replace(str(root), "<project>") for part in command]
            result["cases"].append({
                "chart_version": version, "archive_sha256": digest,
                "values": str(values.relative_to(root)),
                "values_sha256": hashlib.sha256(values.read_bytes()).hexdigest(),
                "helm_lint": {"command": normalized_command, "exit_code": completed.returncode, "stdout": completed.stdout.replace(str(dest), "<extracted-chart>"), "stderr": completed.stderr},
                "shiftscope_report": report,
            })
    output = root / "verification/tool-comparison-results.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(output), "cases": [{"chart": c["chart_version"], "helm_lint_exit": c["helm_lint"]["exit_code"], "shiftscope_rules": [f["rule_id"] for f in c["shiftscope_report"]["findings"]]} for c in result["cases"]]}, indent=2))


if __name__ == "__main__":
    main()
