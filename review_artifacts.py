"""Kong-only artifact collector. Byte integrity is not live-state authentication."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

from upgrade_review import evaluate


class EvidenceError(ValueError):
    pass


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise EvidenceError("Duplicate mapping key")
        result[key] = value
    return result


class StrictLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        pairs = [(self.construct_object(k, deep=deep), self.construct_object(v, deep=deep))
                 for k, v in node.value]
        return unique_pairs(pairs)


def timestamp(value):
    if not isinstance(value, str):
        raise EvidenceError("Capture timestamp is required")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EvidenceError("Invalid capture timestamp") from exc
    if result.tzinfo is None:
        raise EvidenceError("Capture timestamp must include a timezone")
    return result.astimezone(timezone.utc)


def load_artifact(root, spec, now, max_age, evidence):
    if not isinstance(spec, dict) or not isinstance(spec.get("path"), str):
        raise EvidenceError("Artifact path and SHA-256 are required")
    rel = Path(spec["path"])
    if rel.is_absolute() or ".." in rel.parts:
        raise EvidenceError("Artifact path must stay inside the selected root")
    path = (root / rel).resolve()
    if not path.is_relative_to(root):
        raise EvidenceError("Artifact symlink escapes the selected root")
    if not path.is_file() or path.stat().st_size > 2_000_000:
        raise EvidenceError("Artifact is missing, not a regular file, or exceeds 2 MB")
    with path.open("rb") as source:
        data = source.read(2_000_001)
    if len(data) > 2_000_000:
        raise EvidenceError("Artifact exceeds 2 MB")
    digest = hashlib.sha256(data).hexdigest()
    if spec.get("sha256") != digest:
        raise EvidenceError("Artifact SHA-256 does not match")
    captured = timestamp(spec.get("captured_at"))
    age = (now - captured).total_seconds()
    if age < 0 or age > max_age:
        raise EvidenceError("Artifact capture is future-dated or outside the age limit")
    try:
        text = data.decode("utf-8")
        if path.suffix == ".json":
            docs = [json.loads(text, object_pairs_hook=unique_pairs)]
        else:
            depth = 0
            for event in yaml.parse(text):
                if isinstance(event, yaml.AliasEvent):
                    raise EvidenceError("YAML aliases are unsupported")
                if isinstance(event, (yaml.MappingStartEvent, yaml.SequenceStartEvent)):
                    depth += 1
                elif isinstance(event, (yaml.MappingEndEvent, yaml.SequenceEndEvent)):
                    depth -= 1
                if depth > 40:
                    raise EvidenceError("YAML nesting exceeds the prototype limit")
            docs = list(yaml.load_all(text, Loader=StrictLoader))
        if len(docs) > 100:
            raise EvidenceError("Artifact exceeds 100 documents")
    except (yaml.YAMLError, UnicodeError, RecursionError, TypeError) as exc:
        raise EvidenceError("Artifact cannot be parsed safely") from exc
    evidence.append({"path": spec["path"], "sha256": digest,
                     "captured_at": captured.isoformat(), "capture_time_asserted_by_caller": True})
    return docs


def deployment(docs, selector):
    if not isinstance(selector, dict) or not all(
        isinstance(selector.get(k), str) and selector[k] for k in ("name", "namespace")
    ):
        raise EvidenceError("Explicit deployment name and namespace are required")
    found = []
    for index, doc in enumerate(docs):
        if not isinstance(doc, dict) or doc.get("kind") != "Deployment":
            continue
        meta = doc.get("metadata", {})
        if not isinstance(meta, dict):
            raise EvidenceError("Malformed deployment metadata")
        if meta.get("name") == selector["name"] and meta.get("namespace", "default") == selector["namespace"]:
            found.append((index, doc))
    if len(found) != 1:
        raise EvidenceError("Deployment selector must identify exactly one document")
    return found[0]


def containers(doc):
    node = doc
    for key in ("spec", "template", "spec"):
        if not isinstance(node, dict):
            raise EvidenceError("Malformed pod template")
        node = node.get(key)
    items = node.get("containers") if isinstance(node, dict) else None
    if not isinstance(items, list) or not all(isinstance(x, dict) for x in items):
        raise EvidenceError("Pod containers must be a list of objects")
    names = [x.get("name") for x in items]
    if not all(isinstance(n, str) for n in names) or len(names) != len(set(names)):
        raise EvidenceError("Container names must be unique strings")
    return items


def image_tag(image, repositories):
    if not isinstance(image, str) or "@" in image or ":" not in image:
        return None
    repo, tag = image.rsplit(":", 1)
    return tag if repo in repositories else None


def review(case, root, now=None, max_age_seconds=86400):
    """Reject invalid evidence; never turn an invalid artifact into a passing result."""
    report = {"status": "EVIDENCE_REJECTED", "applicability": "UNKNOWN", "satisfaction": "UNKNOWN",
              "evidence": [], "facts": {}, "errors": [], "live_identity_verified": False,
              "chart_render_binding_verified": False,
              "scope": "One Kong requirement; local content and asserted capture times only"}
    root = Path(root).resolve()
    now = now or datetime.now(timezone.utc)
    try:
        if now.tzinfo is None or type(max_age_seconds) is not int or not 1 <= max_age_seconds <= 604800:
            raise EvidenceError("Timezone-aware analysis time and age limit of 1..604800 seconds required")
        if not isinstance(case, dict) or case.get("chart") != "kong/kong":
            raise EvidenceError("Only the declared kong/kong chart is supported")
        evidence = report["evidence"]
        docs = load_artifact(root, case.get("target"), now, max_age_seconds, evidence)
        doc_index, dep = deployment(docs, case.get("proxy"))
        labels = dep["metadata"].get("labels", {})
        if not isinstance(labels, dict) or labels.get("helm.sh/chart") != "kong-" + str(case.get("to_version")):
            raise EvidenceError("Target chart label conflicts with the declared target version")
        items = containers(dep)
        matches = [(i, c) for i, c in enumerate(items) if c["name"] == "proxy"]
        if len(matches) != 1:
            raise EvidenceError("Exactly one proxy container is required")
        ci, proxy = matches[0]
        facts = report["facts"]
        ref = f"{case['target']['path']}#document={doc_index}/spec/template/spec/containers/{ci}"
        facts["proxy_version"] = {"value": image_tag(proxy.get("image"), {"kong", "docker.io/library/kong"}),
                                  "reference": ref + "/image"}
        probe = proxy.get("readinessProbe", {})
        get = probe.get("httpGet", {}) if isinstance(probe, dict) else {}
        path = get.get("path") if isinstance(get, dict) else None
        facts["target_readiness_path"] = {"value": path, "reference": ref + "/readinessProbe/httpGet/path"}

        local = [(i, c) for i, c in enumerate(items) if c["name"] == "ingress-controller"]
        if local:
            if case.get("controller") or case.get("binding"):
                raise EvidenceError("Conflicting colocated and separate-controller evidence")
            i, controller = local[0]
            tag = image_tag(controller.get("image"), {"kong/kubernetes-ingress-controller", "docker.io/kong/kubernetes-ingress-controller"})
            if tag is not None:
                facts["separate_deployments"] = {"value": False, "reference": ref}
                facts["controller_version"] = {"value": tag, "reference": ref.rsplit("/", 1)[0] + f"/{i}/image"}
        elif case.get("controller") and case.get("binding"):
            binding_docs = load_artifact(root, case["binding"], now, max_age_seconds, evidence)
            binding = binding_docs[0]
            if len(binding_docs) != 1 or not isinstance(binding, dict) or binding.get("proxy") != case["proxy"]:
                raise EvidenceError("Controller binding does not match the selected proxy")
            selector = binding.get("controller")
            cds = load_artifact(root, case["controller"], now, max_age_seconds, evidence)
            di, cdep = deployment(cds, selector)
            if selector == case["proxy"]:
                raise EvidenceError("A separate controller must identify a different deployment")
            cc = [c for c in containers(cdep) if c["name"] == "ingress-controller"]
            if len(cc) != 1:
                raise EvidenceError("Exactly one external ingress-controller container is required")
            tag = image_tag(cc[0].get("image"), {"kong/kubernetes-ingress-controller", "docker.io/kong/kubernetes-ingress-controller"})
            cref = f"{case['controller']['path']}#document={di}/spec/template/spec/containers"
            facts["separate_deployments"] = {"value": True, "reference": case["binding"]["path"]}
            facts["controller_version"] = {"value": tag, "reference": cref}
            report["controller_binding_assurance"] = "Checksummed caller assertion, not independently verified routing or ownership"
        elif case.get("controller") or case.get("binding"):
            raise EvidenceError("Separate-controller evidence needs both a manifest and explicit binding")

        outcome = evaluate({"chart": case["chart"], "from_version": case.get("from_version"),
                            "to_version": case.get("to_version"), "facts": facts})
        for key in ("applicability", "satisfaction", "missing_evidence", "reason", "source", "rule_id"):
            report[key] = outcome[key]
        report["status"] = "LOCAL_CONTENT_CHECKED"
        report["limitation"] = (
            "File hashes bind observations to local bytes. They authenticate neither a cluster nor the caller, "
            "capture time, controller relationship, rendered-chart provenance or runtime behavior."
        )
    except (EvidenceError, OSError, ValueError, RecursionError) as exc:
        report.update(status="EVIDENCE_REJECTED", applicability="UNKNOWN", satisfaction="UNKNOWN")
        report["errors"].append(str(exc))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--now", help="Optional explicit analysis timestamp for replay")
    parser.add_argument("--max-age-seconds", type=int, default=86400)
    args = parser.parse_args()
    try:
        if args.case.stat().st_size > 100_000:
            raise EvidenceError("Case file exceeds 100 KB")
        case = json.loads(args.case.read_text(), object_pairs_hook=unique_pairs)
        result = review(case, args.root, timestamp(args.now) if args.now else None, args.max_age_seconds)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Case error: {exc}\n")
    print(json.dumps(result, indent=2))
    # Exit status describes evidence processing, never permission to deploy.
    raise SystemExit(2 if result["status"] == "EVIDENCE_REJECTED" else 0)


if __name__ == "__main__":
    main()
