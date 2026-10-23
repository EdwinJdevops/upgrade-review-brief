"""Compare actual demo reading order with and without the relevance model.

This is an author-run implementation audit, not a relevance or time-saving
benchmark. It uses exactly the same manifests, notes, query and parser in both
arms. It does not search for a more flattering query or assign relevance labels.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from upgrade_brief import build_brief, note_passages, read_checked
from rank_model import LocalReranker, MODEL, REVISION


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    case_bytes = (ROOT / "brief-cases/kong-readiness.json").read_bytes()
    case = json.loads(case_bytes)
    started = time.perf_counter()
    lexical = build_brief(case, ROOT)
    lexical_seconds = time.perf_counter() - started
    started = time.perf_counter()
    scorer = LocalReranker(args.model_dir)
    initialization_seconds = time.perf_counter() - started
    started = time.perf_counter()
    model = build_brief(case, ROOT, scorer)
    model_seconds = time.perf_counter() - started
    unchanged = ("status", "scope", "deployment", "from_chart", "to_chart",
                 "input_identities", "focused_change_query", "changes", "unresolved",
                 "passage_count", "passages_omitted", "generated_actions", "live_identity_verified")
    differences = [key for key in unchanged if model[key] != lexical[key]]
    if differences:
        raise RuntimeError("Unexpected non-ranking differences: " + str(differences))
    identity = lambda report: sorted((p["id"], p["sha256"]) for p in report["source_passages"])
    if identity(model) != identity(lexical):
        raise RuntimeError("Ranking changed source coverage")
    if not all(p["model_executed"] for p in model["source_passages"]):
        raise RuntimeError("Expected every demo passage to be scored by the real model")
    order = lambda report: [p["id"] for p in report["source_passages"]]
    source_order = [p["id"] for p in note_passages(
        read_checked(ROOT, case["notes"], 200_000), case["notes"]["section"])]
    result = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "kind": "author_run_same_input_ablation_not_independent_benchmark",
        "case_sha256": hashlib.sha256(case_bytes).hexdigest(),
        "input_identities": {key: case[key] for key in ("before", "after", "notes")},
        "input_hashes": {key: case[key]["sha256"] for key in ("before", "after", "notes")},
        "model": {"name": MODEL, "revision": REVISION},
        "model_initialized_and_executed": True,
        "source_order": source_order,
        "lexical_order": order(lexical),
        "model_order": order(model),
        "same_top_passage": order(model)[0] == order(lexical)[0],
        "identical_full_order": order(model) == order(lexical),
        "same_non_ranking_report_fields": list(unchanged),
        "same_passage_identities": True,
        "passages_retained_per_arm": model["passage_count"],
        "passages_omitted_per_arm": model["passages_omitted"],
        "model_windows": model["model_calls"],
        "local_timing_seconds": {
            "lexical_report": round(lexical_seconds, 4),
            "model_initialization_including_file_verification": round(initialization_seconds, 4),
            "model_report_after_initialization": round(model_seconds, 4)},
        "timing_scope": "One local execution, lexical first; not a speed benchmark, Render measurement, or total reviewer time.",
        "conclusion_boundary": "The model's demonstrated contribution is reading order and relevance scores/previews. Manifest findings, unknowns and source coverage are deterministic and unchanged. No relevance labels or reviewer outcomes were collected; an order difference cannot establish usefulness."
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
