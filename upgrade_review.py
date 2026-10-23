"""Offline documentation-rule prototype. No model, renderer or cluster access.

Evaluates supplied normalized facts for ONE Kong readiness requirement.
It does not authenticate those facts or approve a deployment.
"""

import argparse
import json
import re
from pathlib import Path

SOURCE = {
    "url": "https://github.com/Kong/charts/blob/main/charts/kong/UPGRADE.md#2260",
    "git_blob_sha": "893527759a66e5293aded6999f8c6879b634c6d6",
    "retrieved_on": "2026-10-20",
    "rule_authorship": "human-authored prototype; not model-generated",
}
LIMITATION = (
    "One documentation rule evaluated against supplied facts only. "
    "Facts are not authenticated; chart packages were not rendered; "
    "runtime behavior and other migration requirements remain unverified."
)


def stable_version(value):
    """Only stable, complete numeric versions; ambiguous tags stay unknown."""
    if not isinstance(value, str) or not re.fullmatch(
        r"v?(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", value
    ):
        return None
    return tuple(int(part) for part in value.removeprefix("v").split("."))


def fact(snapshot, key):
    item = snapshot.get("facts", {}).get(key)
    if not isinstance(item, dict):
        return None
    reference = item.get("reference")
    if not isinstance(reference, str) or not reference.strip():
        return None
    return item.get("value")


def evaluate(snapshot):
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("facts", {}), dict):
        raise ValueError("Input must be an object with an optional facts object.")
    report = {
        "rule_id": "kong-2.26-separate-controller-readiness-v0",
        "source": SOURCE,
        "applicability": "UNKNOWN",
        "satisfaction": "UNKNOWN",
        "missing_evidence": [],
        "reason": "",
        "limitation": LIMITATION,
        "evidence_assurance": "supplied references only; not independently verified",
    }

    def finish(reason, applicability="UNKNOWN", satisfaction="UNKNOWN", missing=()):
        report.update(reason=reason, applicability=applicability,
                      satisfaction=satisfaction, missing_evidence=list(missing))
        return report

    if snapshot.get("chart") != "kong/kong":
        return finish("This prototype supports only the Kong chart; no coverage here.")
    old = stable_version(snapshot.get("from_version"))
    new = stable_version(snapshot.get("to_version"))
    if old is None or new is None:
        return finish("Supply stable source and target chart versions.",
                      missing=("from_version", "to_version"))
    if new != (2, 26, 0) or old >= new:
        return finish("Unsupported transition; this is not a claim that no rule applies.")

    separate = fact(snapshot, "separate_deployments")
    controller = stable_version(fact(snapshot, "controller_version"))
    proxy = stable_version(fact(snapshot, "proxy_version"))
    # A known false conjunct disproves applicability even if other facts are absent.
    if separate is False or (controller is not None and controller[:2] > (2, 10)) or (
        proxy is not None and proxy[:2] < (3, 3)
    ):
        return finish("Supplied facts exclude this specific documented condition.",
                      applicability="NOT_APPLICABLE")

    missing = []
    if type(separate) is not bool:
        missing.append("separate_deployments")
    if controller is None:
        missing.append("controller_version")
    if proxy is None:
        missing.append("proxy_version")
    if missing:
        return finish("Cannot establish applicability from the supplied facts.", missing=missing)

    path = fact(snapshot, "target_readiness_path")
    if path == "/status":
        return finish("Supplied target probe matches this rule's configuration remedy.",
                      applicability="APPLIES", satisfaction="MATCHES_SUPPLIED_FACTS")
    if path == "/status/ready":
        return finish("Affected version combination uses the documented incompatible probe.",
                      applicability="APPLIES", satisfaction="CONTRADICTS_SUPPLIED_FACTS")
    return finish("Need target proxy probe evidence; other endpoints need manual review.",
                  applicability="APPLIES", missing=("target_readiness_path",))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path, help="Normalized JSON facts; see examples")
    args = parser.parse_args()
    try:
        if args.snapshot.stat().st_size > 1_000_000:
            raise ValueError("Snapshot exceeds the prototype's 1 MB input limit.")
        report = evaluate(json.loads(args.snapshot.read_text(encoding="utf-8")))
    except (OSError, ValueError, RecursionError) as exc:
        parser.exit(2, f"Input error: {exc}\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
