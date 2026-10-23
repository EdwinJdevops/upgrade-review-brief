"""Reproduce bounded chart-render observations. Linux x86_64 / WSL2 only.

Downloads only the pinned lab inputs if missing; never connects to a cluster.
No chart hooks or post-renderers are executed. This is a local lab harness,
not a sandbox suitable for arbitrary customer-supplied charts.
"""

import hashlib
import io
import json
import os
import platform
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
LOCK = json.loads((ROOT / "artifact-lock.json").read_text())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def obtain(path):
    item = next(entry for entry in LOCK if entry["path"] == path)
    dest = ROOT / path
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(item["url"], timeout=30) as response:
            data = response.read(item["bytes"] + 1)
        if len(data) != item["bytes"] or sha(data) != item["sha256"]:
            raise RuntimeError("Downloaded input does not match lock: " + path)
        dest.write_bytes(data)
    if sha(dest.read_bytes()) != item["sha256"]:
        raise RuntimeError("Local input does not match lock: " + path)
    return dest


def helm_binary():
    if platform.system() != "Linux" or platform.machine() not in ("x86_64", "AMD64"):
        raise RuntimeError("This pinned Helm binary is Linux x86_64. Use WSL2 Ubuntu.")
    dest = ROOT / "tools/helm"
    if not dest.exists():
        archive = obtain("tools/helm-v3.12.3-linux-amd64.tar.gz")
        with tarfile.open(fileobj=io.BytesIO(archive.read_bytes()), mode="r:gz") as package:
            member = package.getmember("linux-amd64/helm")
            if not member.isfile() or member.size > 60_000_000:
                raise RuntimeError("Unexpected Helm archive member")
            data = package.extractfile(member).read()
        dest.write_bytes(data)
        dest.chmod(0o700)
    record = next(entry for entry in LOCK if entry["path"] == "tools/helm")
    if sha(dest.read_bytes()) != record["sha256"]:
        raise RuntimeError("Helm executable does not match lock")
    return dest


def render(helm, name, archive_path, values, kube_version):
    archive = obtain(archive_path)
    vp = ROOT / "inputs" / (name + ".yaml")
    vp.write_text(yaml.safe_dump(values))
    cmd = [str(helm), "template", "upgrade-review", str(archive), "--namespace", "review",
           "--kube-version", kube_version, "--is-upgrade", "--values", str(vp)]
    env = dict(os.environ)
    env.update(KUBECONFIG="/dev/null", HELM_CONFIG_HOME=str(ROOT / "tools/config"),
               HELM_CACHE_HOME=str(ROOT / "tools/cache"), HELM_DATA_HOME=str(ROOT / "tools/data"))
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=env)
    if result.returncode:
        raise RuntimeError(name + ": " + result.stderr)
    out = ROOT / "outputs" / (name + ".yaml")
    out.write_text(result.stdout)
    docs = [d for d in yaml.safe_load_all(result.stdout) if isinstance(d, dict)]
    command = [str(Path(c).relative_to(ROOT)) if c.startswith(str(ROOT) + "/") else c for c in cmd]
    return docs, {"case": name, "input_chart": archive_path,
                  "input_sha256": sha(archive.read_bytes()), "values_sha256": sha(vp.read_bytes()),
                  "output": str(out.relative_to(ROOT)), "output_sha256": sha(out.read_bytes()),
                  "command": command, "kube_version": kube_version, "runtime_verified": False}


def main():
    (ROOT / "outputs").mkdir(exist_ok=True)
    helm = helm_binary()
    results = []
    cases = [
        ("kong-old-proxy-only", "2.25.0", False, "2.10.4", "3.3.0", None, "/status"),
        ("kong-new-proxy-only", "2.26.0", False, "2.10.4", "3.3.0", None, "/status/ready"),
        ("kong-new-override", "2.26.0", False, "2.10.4", "3.3.0", "/status", "/status"),
        ("kong-new-colocated-old-controller", "2.26.0", True, "2.10.4", "3.3.0", None, "/status"),
        ("kong-new-older-proxy", "2.26.0", False, "2.10.4", "3.2.0", None, "/status"),
        ("kong-new-proxy-only-new-controller-setting", "2.26.0", False, "2.11.0", "3.3.0", None, "/status/ready"),
    ]
    for name, version, enabled, controller, proxy, override, expected in cases:
        values = {"image": {"tag": proxy}, "ingressController": {"enabled": enabled, "image": {"tag": controller}},
                  "postgresql": {"enabled": False}, "env": {"database": "off"}}
        if override:
            values["readinessProbe"] = {"httpGet": {"path": override}}
        docs, record = render(helm, name, f"inputs/kong-{version}.tgz", values, "1.27.3")
        proxies = [(i, d, c) for i, d in enumerate(docs) if d.get("kind") == "Deployment"
                   for c in d["spec"]["template"]["spec"]["containers"] if c["name"] == "proxy"]
        if len(proxies) != 1:
            raise RuntimeError("Expected exactly one proxy container")
        i, deployment, container = proxies[0]
        actual = container["readinessProbe"]["httpGet"]["path"]
        if actual != expected:
            raise AssertionError(f"{name}: expected {expected}, got {actual}")
        record.update(rendered_readiness=container["readinessProbe"]["httpGet"], image=container["image"],
                      assertion="rendered readiness path equals documented case expectation",
                      observation_pass=True, controller_colocated=enabled,
                      external_controller_verified=False,
                      note="A disabled controller image setting is not evidence of an external deployment.")
        results.append(record)

    for name, values, image in [
        ("ksm-default", {}, "v2.13.0"),
        ("ksm-image-override", {"image": {"tag": "v2.14.0"}}, "v2.14.0"),
        ("ksm-self-monitor", {"image": {"tag": "v2.14.0"}, "selfMonitor": {"enabled": True}}, "v2.14.0"),
    ]:
        docs, record = render(helm, name, "inputs/kube-state-metrics-5.26.0.tgz", values, "1.29.10")
        deps = [d for d in docs if d.get("kind") == "Deployment"]
        if len(deps) != 1:
            raise RuntimeError("Expected exactly one kube-state-metrics deployment")
        container = deps[0]["spec"]["template"]["spec"]["containers"][0]
        probe = container["readinessProbe"]["httpGet"]
        if not container["image"].endswith(":" + image) or probe["port"] != 8080 or probe["path"] != "/readyz":
            raise AssertionError(name + ": unexpected rendered image/probe")
        record.update(image=container["image"], rendered_readiness=probe,
                      container_ports=container.get("ports"), observation_pass=True,
                      assertion="rendered image is expected and readiness remains /readyz on 8080",
                      note="This confirms manifest configuration, not HTTP behavior or a universal remedy.")
        results.append(record)

    meta = {"helm_version": subprocess.check_output([str(helm), "version", "--short"], text=True).strip(),
            "python_version": sys.version.split()[0], "pyyaml_version": yaml.__version__,
            "cases": len(results), "observation_assertions_passed": sum(r["observation_pass"] for r in results),
            "model_calls": 0, "cluster_runtime_tests": 0,
            "configuration_origin": "author-controlled lab inputs using official published chart packages",
            "results": results}
    (ROOT / "outputs/experiment-results.json").write_text(json.dumps(meta, indent=2) + "\n")
    for result in results:
        print(result["case"], result["rendered_readiness"], "observation PASS")
    print(f"{len(results)} render observations passed; zero runtime or model tests.")


if __name__ == "__main__":
    main()
