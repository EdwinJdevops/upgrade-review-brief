"""Build a local, source-linked migration review brief from two manifests."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

import yaml

from review_artifacts import EvidenceError, StrictLoader, containers, deployment, unique_pairs

SCOPE = "One explicitly selected Deployment; image, HTTP probe path/port and read-only-root settings only"


def read_checked(root, spec, limit):
    if not isinstance(spec, dict) or not isinstance(spec.get("path"), str):
        raise EvidenceError("A relative path and expected SHA-256 are required")
    rel = Path(spec["path"])
    path = (root / rel).resolve()
    if rel.is_absolute() or ".." in rel.parts or not path.is_relative_to(root):
        raise EvidenceError("Input path escapes selected root")
    if not path.is_file() or path.stat().st_size > limit:
        raise EvidenceError("Input missing or too large")
    with path.open("rb") as f:
        raw = f.read(limit + 1)
    if len(raw) > limit or hashlib.sha256(raw).hexdigest() != spec.get("sha256"):
        raise EvidenceError("Input too large or SHA-256 mismatch")
    return raw.decode("utf-8")


def parse_manifests(text):
    depth = 0
    count = 0
    for event in yaml.parse(text):
        if isinstance(event, yaml.AliasEvent):
            raise EvidenceError("YAML aliases are unsupported")
        if isinstance(event, yaml.DocumentStartEvent):
            count += 1
        if isinstance(event, (yaml.MappingStartEvent, yaml.SequenceStartEvent)):
            depth += 1
        if isinstance(event, (yaml.MappingEndEvent, yaml.SequenceEndEvent)):
            depth -= 1
        if depth > 40 or count > 100:
            raise EvidenceError("Manifest depth or document count exceeds limit")
    return list(yaml.load_all(text, Loader=StrictLoader))


def snapshot(text, selector):
    index, doc = deployment(parse_manifests(text), selector)
    labels = doc["metadata"].get("labels", {})
    if not isinstance(labels, dict):
        raise EvidenceError("Deployment labels must be a mapping")
    chart = labels.get("helm.sh/chart")
    if not isinstance(chart, str) or len(chart) > 200:
        raise EvidenceError("Explicit Helm chart label required")
    result = {"chart_label": chart, "document_index": index, "containers": {}}
    for container in containers(doc):
        name = container["name"]
        item = {}
        image = container.get("image")
        if not isinstance(image, str) or len(image) > 500:
            raise EvidenceError("A bounded image string is required")
        item["image"] = image
        context = container.get("securityContext", {})
        if not isinstance(context, dict):
            raise EvidenceError("Malformed security context")
        readonly = context.get("readOnlyRootFilesystem")
        if readonly is not None and type(readonly) is not bool:
            raise EvidenceError("readOnlyRootFilesystem must be boolean")
        item["readOnlyRootFilesystem"] = readonly
        for probe_name in ("readinessProbe", "livenessProbe", "startupProbe"):
            probe = container.get(probe_name, {})
            if not isinstance(probe, dict):
                raise EvidenceError("Malformed probe")
            http = probe.get("httpGet", {})
            if not isinstance(http, dict):
                raise EvidenceError("Malformed HTTP probe")
            for field in ("path", "port"):
                value = http.get(field)
                if value is not None and (type(value) not in (str, int) or len(str(value)) > 500):
                    raise EvidenceError("Unsupported probe field value")
                item[f"{probe_name}.httpGet.{field}"] = value
        result["containers"][name] = item
    return result


def difference(before, after):
    changes = []
    for name in sorted(set(before["containers"]) | set(after["containers"])):
        old = before["containers"].get(name)
        new = after["containers"].get(name)
        if old is None or new is None:
            changes.append({"field": f"containers/{name}", "before": old, "after": new})
            continue
        for field in sorted(old):
            if old[field] != new[field]:
                changes.append({"field": f"containers/{name}/{field}", "before": old[field], "after": new[field]})
    return changes


def note_passages(text, requested_section):
    if not isinstance(requested_section, str) or not requested_section.strip():
        raise EvidenceError("Explicit migration section heading required")
    lines = text.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if re.fullmatch(r"#{2} " + re.escape(requested_section) + r"\s*", line)]
    if len(matches) != 1:
        raise EvidenceError("Section must match exactly one level-two heading")
    start = matches[0] + 1
    end = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines))
    spans = []
    block_start = None
    in_fence = False
    for i in range(start, end):
        stripped = lines[i].strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
        if stripped and block_start is None:
            block_start = i
        if not stripped and not in_fence and block_start is not None:
            spans.append((block_start, i))
            block_start = None
    if block_start is not None:
        spans.append((block_start, end))
    if in_fence or not spans or len(spans) > 16:
        raise EvidenceError("Section empty, has unmatched code fence, or exceeds 16 passages")
    grouped = []
    for lo, hi in spans:
        # Keep configuration examples with their preceding explanatory paragraph.
        if lines[lo].lstrip().startswith(("```", "~~~")) and grouped:
            grouped[-1] = (grouped[-1][0], hi)
        else:
            grouped.append((lo, hi))
    passages = []
    for lo, hi in grouped:
        passage = "".join(lines[lo:hi]).rstrip("\r\n")
        if len(passage) > 10000:
            raise EvidenceError("Source passage exceeds limit")
        passages.append({"id": f"L{lo+1}-L{hi}", "start_line": lo+1, "end_line": hi,
                         "text": passage, "sha256": hashlib.sha256(passage.encode()).hexdigest()})
    return passages


def lexical_score(query, passage):
    words = lambda value: set(re.findall(r"[a-z0-9_]+", value.lower()))
    return len(words(query) & words(passage))


def build_brief(case, root, scorer=None):
    root = Path(root).resolve()
    if not isinstance(case, dict) or case.get("schema_version") != 1:
        raise EvidenceError("Unsupported brief case schema")
    old = snapshot(read_checked(root, case.get("before"), 2_000_000), case.get("deployment"))
    new = snapshot(read_checked(root, case.get("after"), 2_000_000), case.get("deployment"))
    if old["chart_label"] != case.get("from_chart") or new["chart_label"] != case.get("to_chart"):
        raise EvidenceError("Declared chart versions do not match supplied manifest labels")
    source = case.get("notes")
    if not isinstance(source, dict):
        raise EvidenceError("Missing notes source")
    parsed_url = urlsplit(source.get("url", ""))
    url = source.get("url", "")
    if (not isinstance(url, str) or len(url) > 2048 or any(c.isspace() or ord(c) < 32 for c in url)
            or parsed_url.scheme != "https" or not parsed_url.hostname or parsed_url.username or parsed_url.password):
        raise EvidenceError("Source URL must be HTTPS without embedded credentials")
    text = read_checked(root, source, 200_000)
    passages = note_passages(text, source.get("section"))
    changes = difference(old, new)
    # Narrow query: no Secrets, env values, annotations, headers, commands or full manifest bodies.
    query = "Kubernetes Helm upgrade " + old["chart_label"] + " to " + new["chart_label"] + ". " + "; ".join(
        f"{c['field']} changes from {json.dumps(c['before'])} to {json.dumps(c['after'])}" for c in changes
    )
    if not changes:
        query += " No changes in the limited selected fields. Which migration prerequisites still require human review?"
    if len(query) > 10000:
        raise EvidenceError("Focused change query exceeds model input limit")
    results = []
    for passage in passages:
        ranking = scorer.score(query, passage["text"]) if scorer is not None else {
            "score": lexical_score(query, passage["text"]), "model_executed": False, "reason": "lexical_comparison_baseline"}
        results.append({k:v for k,v in passage.items() if k != "text"} | {
            "source_path": source["path"], "source_url": source["url"],
            "lexical_overlap": lexical_score(query, passage["text"]), **ranking})
    results.sort(key=lambda x: (x["score"] is not None, x["score"] if x["score"] is not None else 0), reverse=True)
    # Allocate the bounded literal previews after ranking, so the first reading
    # does not lose its preview merely because it appeared later in the source.
    texts = {passage["id"]: passage["text"] for passage in passages}
    quote_budget = 12
    for result in results:
        text = texts[result["id"]]
        count = min(6, quote_budget, len(text.split()))
        match = re.match(r"(?:\s*\S+){1," + str(count) + r"}", text) if count else None
        result["exact_excerpt"] = match.group(0) if match else ""
        quote_budget -= count
    unresolved = ["This brief does not verify a live cluster, a supported upgrade path or runtime readiness.",
                  "Only the explicitly selected source section and Deployment fields were considered.",
                  "Every source passage remains listed; relevance scores are neither applicability nor approval."]
    if "ingress-controller" not in new["containers"] and any("readinessProbe" in c["field"] for c in changes):
        unresolved.append("No colocated ingress-controller appears in the selected Deployment. An external controller's version and relationship are not established by this input.")
    return {"status": "REVIEW_REQUIRED", "scope": SCOPE, "mode": "open_weight_reranker" if scorer is not None else "lexical_baseline",
            "deployment": case["deployment"], "from_chart": old["chart_label"], "to_chart": new["chart_label"],
            "input_identities": {key: case[key] for key in ("before", "after", "notes")},
            "focused_change_query": query, "changes": changes, "source_passages": results,
            "passage_count": len(passages), "passages_omitted": 0,
            "model_calls": sum(r.get("window_count", int(bool(r["model_executed"]))) for r in results), "unresolved": unresolved,
            "generated_actions": [], "live_identity_verified": False}


def markdown(report):
    def safe(value):
        text = str(value).replace("`", "'").replace("\r", " ").replace("\n", " ").replace("<", "&lt;").replace(">", "&gt;")
        return text.replace("[", "\\[").replace("]", "\\]")
    lines = ["# Upgrade review brief", "", "**REVIEW REQUIRED**", "", safe(report["scope"]), "",
             f"{safe(report['from_chart'])} → {safe(report['to_chart'])}", "", "## Focused manifest changes", ""]
    for change in report["changes"]:
        lines.append(f"- `{safe(change['field'])}`: `{safe(json.dumps(change['before']))}` → `{safe(json.dumps(change['after']))}`")
    if not report["changes"]:
        lines.append("No difference in the limited selected fields. Other changes may exist.")
    lines += ["", "## Migration passages, ordered for review", "", "All selected-section passages are retained. Scores are relative relevance, not confidence.", ""]
    for passage in report["source_passages"]:
        lines += [f"- **{safe(passage['id'])}** · score `{passage['score']}` · `{safe(passage['source_path'])}`", 
                  f"  Source: {safe(passage['source_url'])}", f"  Excerpt preview: {safe(passage['exact_excerpt'])}" if passage["exact_excerpt"] else "  Read the recorded source lines; excerpt budget exhausted."]
    lines += ["", "## Unresolved", ""] + ["- " + safe(x) for x in report["unresolved"]]
    lines += ["", f"Mode: {report['mode']}; model calls: {report['model_calls']}; omitted passages: {report['passages_omitted']}.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path)
    parser.add_argument("--lexical-baseline", action="store_true")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args()
    if bool(args.model_dir) == args.lexical_baseline:
        parser.error("Choose exactly one of --model-dir and --lexical-baseline")
    try:
        if args.case.stat().st_size > 100_000:
            raise EvidenceError("Case file exceeds 100 KB")
        case = json.loads(args.case.read_text(), object_pairs_hook=unique_pairs)
        # Validate inputs before loading weights or running inference.
        build_brief(case, args.root)
        scorer = None
        if args.model_dir:
            from rank_model import LocalReranker, MODEL, REVISION
            scorer = LocalReranker(args.model_dir)
        result = build_brief(case, args.root, scorer)
        if scorer is not None:
            result["model"] = {"name": MODEL, "revision": REVISION, "runtime": "local_cpu_float32"}
        print(json.dumps(result, indent=2) if args.format == "json" else markdown(result))
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError, RecursionError) as exc:
        parser.exit(2, f"Brief could not be produced: {exc}\n")
    # Successful report generation never signals operational approval.
    return 0


if __name__ == "__main__":
    sys.exit(main())
