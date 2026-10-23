"""Bounded version-range selection and independent reading tasks per change.

Selection identifies headings in supplied bytes, never authenticates a guide or
certifies that a passage applies. Scores stay within their individual query.
"""
import hashlib
import re
from urllib.parse import urlsplit, urlunsplit

from review_artifacts import EvidenceError
from upgrade_brief import SCOPE, difference, lexical_score

MAX_PASSAGES = 128
MAX_QUERIES = 6


def source_line_url(url, first, last):
    parsed = urlsplit(url)
    if parsed.hostname == "github.com" and re.match(r"^/[^/]+/[^/]+/blob/[^/]+/.+", parsed.path):
        return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, f"L{first}-L{last}"))
    return url


def chart_version(label):
    match = re.fullmatch(r"(.+)-(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", label)
    if not match:
        raise EvidenceError("Range selection requires stable chart-name-X.Y.Z labels; use an explicit section for other formats")
    return match[1], tuple(int(match[i]) for i in (2, 3, 4))


def sections(text):
    lines = text.splitlines(keepends=True)
    headings = []
    fence = None
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        marker = re.match(r"(`{3,}|~{3,})", stripped)
        if marker:
            value = marker[1]
            if fence is None:
                fence = value
            elif value[0] == fence[0] and len(value) >= len(fence) and not stripped[len(value):].strip():
                fence = None
            continue
        if fence is None:
            heading = re.fullmatch(r"## ([^\r\n]+?)[ \t]*(?:\r?\n)?", line)
            if heading:
                headings.append((i, heading[1]))
    if fence is not None:
        raise EvidenceError("Guide contains an unmatched code fence")
    if not headings or len(headings) > 100:
        raise EvidenceError("Range selection requires 1–100 level-two headings")
    if len({name for _, name in headings}) != len(headings):
        raise EvidenceError("Duplicate migration section headings are ambiguous")
    return lines, [(name, pos + 1, headings[n+1][0] if n+1 < len(headings) else len(lines))
                   for n, (pos, name) in enumerate(headings)]


def passages_in(lines, lo, hi, heading):
    spans = []
    start = None
    fence = None
    for i in range(lo, hi):
        stripped = lines[i].strip()
        marker = re.match(r"(`{3,}|~{3,})", stripped)
        if marker:
            value = marker[1]
            if fence is None:
                fence = value
            elif value[0] == fence[0] and len(value) >= len(fence) and not stripped[len(value):].strip():
                fence = None
        if stripped and start is None:
            start = i
        if not stripped and fence is None and start is not None:
            spans.append((start, i))
            start = None
    if start is not None:
        spans.append((start, hi))
    grouped = []
    for a, b in spans:
        if lines[a].lstrip().startswith(("```", "~~~")) and grouped:
            grouped[-1] = (grouped[-1][0], b)
        else:
            grouped.append((a, b))
    result = []
    for a, b in grouped:
        value = "".join(lines[a:b]).rstrip("\r\n")
        if len(value) > 10000:
            raise EvidenceError("A selected source passage exceeds 10000 characters")
        result.append({"id": f"L{a+1}-L{b}", "start_line": a+1, "end_line": b,
                       "section": heading, "text": value,
                       "sha256": hashlib.sha256(value.encode()).hexdigest()})
    return result


def select_range(text, before, after):
    chart, low = chart_version(before)
    other, high = chart_version(after)
    if chart != other or low >= high:
        raise EvidenceError("Range selection requires the same chart and a strictly increasing stable version")
    lines, available = sections(text)
    chosen, ledger = [], []
    first_heading_line = available[0][1] - 1
    if first_heading_line > 0 and any(line.strip() for line in lines[:first_heading_line]):
        ledger.append({"heading": "Document preamble", "start_line": 0, "end_line": first_heading_line,
                       "included": False, "reason": "outside_level_two_sections_review_separately"})
    for name, lo, hi in available:
        version = re.fullmatch(r"v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", name)
        if version:
            included = low < tuple(map(int, version.groups())) <= high
            reason = "inside_declared_version_range" if included else "outside_declared_version_range"
        else:
            included = name.lower() != "table of contents"
            reason = "unversioned_context_requires_review" if included else "table_of_contents"
        ledger.append({"heading": name, "start_line": lo, "end_line": hi,
                       "included": included, "reason": reason})
        if included:
            chosen.extend(passages_in(lines, lo, hi, name))
    if not chosen or len(chosen) > MAX_PASSAGES:
        raise EvidenceError("Range selection must contain 1–128 passages; use a narrower explicit section")
    # Score release-specific passages before generic context if a budget runs out.
    chosen.sort(key=lambda p: (not bool(re.fullmatch(r"v?\d+\.\d+\.\d+", p["section"])), p["start_line"]))
    return chosen, {"mode": "version_range", "from_chart": before, "to_chart": after,
                    "rule": "Select stable X.Y.Z headings with from < heading <= to; retain all non-version sections except Table of contents.",
                    "sections": ledger, "guide_authenticity_verified": False,
                    "version_history_complete_verified": False,
                    "warning": "Only supplied level-two sections are considered; document preamble is excluded and requires separate review. Missing releases, differently formatted headings and application-version prerequisites need human verification. Unversioned sections are retained, not declared applicable."}


def change_query(change, before, after):
    field = change["field"]
    if "readOnlyRootFilesystem" in field:
        question = "Which migration conditions concern a container filesystem becoming read-only, extensions writing files, or required writable mounts?"
    elif "Probe.httpGet.path" in field:
        question = "Which migration conditions concern changed health-check endpoints, readiness or liveness, and prerequisites for becoming healthy?"
    elif "Probe.httpGet.port" in field:
        question = "Which migration conditions concern the health-check listener port and prerequisites for reaching it?"
    else:
        question = "Which migration conditions concern this container or image change and its upgrade prerequisites?"
    import json
    return f"Helm chart {before} to {after}. {field}: {json.dumps(change['before'])} -> {json.dumps(change['after'])}. {question}"


def build_range_brief(case, old, new, source, text, scorer):
    passages, coverage = select_range(text, old["chart_label"], new["chart_label"])
    changes = difference(old, new)
    queried = changes[:MAX_QUERIES]
    queries = [{"field": c["field"], "query": change_query(c, old["chart_label"], new["chart_label"])} for c in queried]
    if not queries:
        queries = [{"field": "general_prerequisites", "query": f"Helm upgrade {old['chart_label']} to {new['chart_label']}. Which migration prerequisites require review even when the selected manifest fields do not change?"}]
    if any(len(task["query"]) > 10000 for task in queries):
        raise EvidenceError("A focused change query exceeds the supported input limit")
    scores = [[] for _ in queries]
    remaining = 32
    # Interleave queries so one field cannot consume the entire shared budget.
    for p in passages:
        for i, task in enumerate(queries):
            if scorer is None:
                result = {"score": lexical_score(task["query"], p["text"]), "model_executed": False,
                          "reason": "lexical_comparison_baseline", "window_count": 0}
            elif remaining <= 0:
                result = {"score": None, "model_executed": False, "window_count": 0,
                          "reason": "request_window_budget_exhausted"}
            else:
                result = scorer.score(task["query"], p["text"], window_limit=remaining)
                used = result.get("window_count", 0)
                if type(used) is not int or not 0 <= used <= remaining:
                    raise ValueError("Model exceeded the shared window budget")
                remaining -= used
            scores[i].append({"id": p["id"], "section": p["section"], **result})
    tasks = []
    for task, results in zip(queries, scores):
        results.sort(key=lambda r: (r["score"] is not None, r["score"] if r["score"] is not None else 0), reverse=True)
        tasks.append(task | {"readings": results, "scored_passages": sum(r["score"] is not None for r in results),
                             "unscored_passages": sum(r["score"] is None for r in results)})
    # Put each change's first scored reading within reach, without comparing
    # logits from different queries or hiding the remaining source material.
    ids = [r["id"] for t in tasks for r in t["readings"][:1] if r["score"] is not None]
    ids += [p["id"] for p in sorted(passages, key=lambda p: p["start_line"])]
    by_id = {p["id"]: p for p in passages}
    ordered = []
    budget = 12
    for identifier in dict.fromkeys(ids):
        p = by_id[identifier]
        count = min(6, budget, len(p["text"].split()))
        match = re.match(r"(?:\s*\S+){1," + str(count) + r"}", p["text"]) if count else None
        excerpt = match[0] if match else ""
        budget -= count
        ordered.append({k: v for k, v in p.items() if k != "text"} | {
            "source_path": source["path"], "source_url": source["url"], "exact_excerpt": excerpt,
            "source_line_url": source_line_url(source["url"], p["start_line"], p["end_line"]),
            "score": None, "model_executed": any(r["id"] == identifier and r["model_executed"] for group in scores for r in group),
            "reason": "See independent per-change reading scores; scores from different queries are not combined."})
    coverage.update({"changes_total": len(changes), "changes_queried": len(queried),
                     "changes_without_dedicated_query": [c["field"] for c in changes[MAX_QUERIES:]],
                     "model_window_budget": 32,
                     "unscored_query_passage_pairs": sum(t["unscored_passages"] for t in tasks)})
    return {"status": "REVIEW_REQUIRED", "scope": SCOPE, "mode": "open_weight_per_change" if scorer else "lexical_per_change",
            "deployment": case["deployment"], "from_chart": old["chart_label"], "to_chart": new["chart_label"],
            "input_identities": {key: case[key] for key in ("before", "after", "notes")},
            "focused_change_query": "Independent queries per selected-field change; see reading_tasks.",
            "changes": changes, "source_passages": ordered, "reading_tasks": tasks, "coverage": coverage,
            "passage_count": len(passages), "passages_omitted": 0,
            "model_calls": sum(r.get("window_count", 0) for group in scores for r in group),
            "unresolved": ["This brief does not verify a live cluster, a supported upgrade path or runtime readiness.",
                "Version-range selection covers supplied stable release headings and unversioned context; it does not prove complete migration history.",
                "External component versions, relationships and prerequisite completion are not established by the selected Deployment.",
                "Per-change rankings are reading suggestions, not extracted obligations, applicability decisions or approval.",
                "Inspect the section ledger and every unscored item; unsupported fields and other resources may contain essential changes."],
            "generated_actions": [], "live_identity_verified": False}
