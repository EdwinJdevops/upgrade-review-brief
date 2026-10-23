"""Reproduce a controlled two-change render from pinned official chart archives.

Runs Helm template offline with an empty kubeconfig. No cluster connections,
hooks or post-renderers execute. Historical versions are research inputs.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiment.run_render_experiment import helm_binary, obtain
from upgrade_brief import snapshot

URL = "https://github.com/Kong/charts/releases/download/kong-2.18.0/kong-2.18.0.tgz"
DIGEST = "85e687471e16bf4b1c7887aae53d0e2c29111105f33ac963c813dc6ad67d52f9"


def main():
    archive = ROOT / "experiment/inputs/kong-2.18.0.tgz"
    if not archive.exists():
        with urllib.request.urlopen(URL, timeout=45) as response:
            data = response.read(2_000_001)
        if len(data) > 2_000_000 or hashlib.sha256(data).hexdigest() != DIGEST:
            raise ValueError("Archive differs from publisher-index digest")
        archive.write_bytes(data)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != DIGEST:
        raise ValueError("Local archive differs from pinned digest")
    helm = helm_binary()
    target = obtain("inputs/kong-2.26.0.tgz")
    values_path = ROOT / "experiment/inputs/kong-new-proxy-only.yaml"
    selector = {"name": "upgrade-review-kong", "namespace": "review"}
    records = []
    for name, chart in (("before", archive), ("after", target)):
        command = [str(helm), "template", "upgrade-review", str(chart), "--namespace", "review",
                   "--kube-version", "1.27.3", "--is-upgrade", "--values", str(values_path)]
        env = dict(os.environ, KUBECONFIG="/dev/null",
                   HELM_CONFIG_HOME=str(ROOT / "experiment/tools/config"),
                   HELM_CACHE_HOME=str(ROOT / "experiment/tools/cache"),
                   HELM_DATA_HOME=str(ROOT / "experiment/tools/data"))
        process = subprocess.run(command, text=True, capture_output=True, check=True, timeout=45, env=env)
        path = ROOT / f"experiment/outputs/kong-range-{name}.yaml"
        path.write_text(process.stdout)
        facts = snapshot(process.stdout, selector)
        records.append({"role": name, "path": str(path.relative_to(ROOT)),
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "chart_archive_sha256": hashlib.sha256(chart.read_bytes()).hexdigest(),
                        "snapshot": facts, "command": [str(Path(x).relative_to(ROOT)) if x.startswith(str(ROOT)+"/") else x for x in command],
                        "stderr": process.stderr})
    guide = ROOT / "model-evaluation/sources/kong-guide.md"
    notes = {"path": str(guide.relative_to(ROOT)), "sha256": hashlib.sha256(guide.read_bytes()).hexdigest(),
             "url": "https://github.com/Kong/charts/blob/main/charts/kong/UPGRADE.md", "selection": "version_range"}
    case = {"schema_version": 1, "deployment": selector,
            "from_chart": records[0]["snapshot"]["chart_label"], "to_chart": records[1]["snapshot"]["chart_label"],
            **{r["role"]: {"path": r["path"], "sha256": r["sha256"]} for r in records}, "notes": notes}
    (ROOT / "brief-cases/kong-range.json").write_text(json.dumps(case, indent=2)+"\n")
    evidence = {"kind": "controlled_official_chart_render_not_live_upgrade", "chart_index": "https://charts.konghq.com/index.yaml",
                "historical_before_archive": URL, "before_archive_sha256": DIGEST,
                "values_path": str(values_path.relative_to(ROOT)), "values_sha256": hashlib.sha256(values_path.read_bytes()).hexdigest(),
                "helm": subprocess.check_output([str(helm), "version", "--short"], text=True).strip(),
                "runtime_verified": False, "records": records}
    (ROOT / "verification/range-render-2026-10-23.json").write_text(json.dumps(evidence, indent=2)+"\n")
    print(json.dumps({"from":case["from_chart"],"to":case["to_chart"],"containers":[r["snapshot"]["containers"] for r in records]}, indent=2))


if __name__ == "__main__":
    main()
