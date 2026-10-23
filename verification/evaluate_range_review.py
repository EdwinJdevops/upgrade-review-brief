"""Frozen author-labeled comparison on the controlled multi-change render.

Uses the same candidates for all arms. Labels identify two prerequisite passages,
not live applicability or human review outcomes. Results are not independent.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from upgrade_brief import build_brief, difference, read_checked, snapshot
from review_plan import select_range
from rank_model import LocalReranker, MODEL, REVISION


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay-contract", type=Path,
                        help="Replay the original case metadata from a frozen contract, including its historical source URL")
    parser.add_argument("--output", type=Path, default=ROOT / "verification/range-evaluation-replay.json")
    parser.add_argument("--report-output", type=Path, default=ROOT / "verification/range-demo-replay.json")
    args = parser.parse_args()
    case = (json.loads(args.replay_contract.read_text())["case"] if args.replay_contract else
            json.loads((ROOT / "brief-cases/kong-range.json").read_text()))
    old = snapshot(read_checked(ROOT, case["before"], 200_000), case["deployment"])
    new = snapshot(read_checked(ROOT, case["after"], 200_000), case["deployment"])
    passages, _ = select_range(read_checked(ROOT,case["notes"],200_000),case["from_chart"],case["to_chart"])
    changes = difference(old,new)
    combined = "Kubernetes Helm upgrade " + case["from_chart"] + " to " + case["to_chart"] + ". " + "; ".join(
        f"{c['field']} changes from {json.dumps(c['before'])} to {json.dumps(c['after'])}" for c in changes)
    expected = {"containers/proxy/readOnlyRootFilesystem":"L124-L132", "containers/proxy/readinessProbe.httpGet.path":"L89-L97"}
    contract = {"case":case,"candidate_sha256":{p["id"]:p["sha256"] for p in passages},
                "expected_prerequisite_passage_by_field":expected,"combined_query":combined,
                "metric":"Coverage of two author-labeled prerequisite passages with four reading slots: combined top four, or top two for each changed field. Also report per-field hit@2.",
                "scope":"One controlled same-chart historical render; author labels, no independent engineer or timing outcomes. Not general accuracy or incident prevention."}
    encoded = json.dumps(contract,indent=2)+"\n"
    frozen = ROOT / "verification/range-evaluation-contract.json"
    if frozen.exists() and frozen.read_text()!=encoded:
        raise ValueError("Do not overwrite frozen evaluation inputs")
    if not frozen.exists():
        frozen.write_text(encoded)
    model = LocalReranker(ROOT/".models/bge-reranker-base")
    started=time.perf_counter()
    report=build_brief(case,ROOT,model)
    seconds=time.perf_counter()-started
    baseline=build_brief(case,ROOT)
    combined_scores=[{"id":p["id"],**model.score(combined,p["text"])} for p in passages]
    combined_scores.sort(key=lambda r:r["score"] if r["score"] is not None else float('-inf'),reverse=True)
    combined_ids=[r["id"] for r in combined_scores[:4]]
    def summarize(value):
        slots=[r["id"] for t in value["reading_tasks"] for r in t["readings"][:2] if r["score"] is not None]
        return {"reading_slots":slots,"prerequisite_passages_covered":sorted(set(slots)&set(expected.values())),
                "per_field_hit_at_2":{t["field"]:expected[t["field"]] in [r["id"] for r in t["readings"][:2] if r["score"] is not None] for t in value["reading_tasks"]},
                "ranking_by_field":{t["field"]:[r["id"] for r in t["readings"] if r["score"] is not None] for t in value["reading_tasks"]}}
    result={"checked_at":datetime.now(timezone.utc).isoformat(),"contract_sha256":hashlib.sha256(encoded.encode()).hexdigest(),
            "model":{"name":MODEL,"revision":REVISION},"actual_model":True,"test_double":False,
            "combined_model":{"reading_slots":combined_ids,"prerequisite_passages_covered":sorted(set(combined_ids)&set(expected.values()))},
            "per_change_model":summarize(report),"per_change_lexical":summarize(baseline),
            "selected_passages":report["passage_count"],"passages_omitted":report["passages_omitted"],
            "model_windows":report["model_calls"],"unscored_query_passage_pairs":report["coverage"]["unscored_query_passage_pairs"],
            "local_report_seconds_excluding_model_initialization":round(seconds,4),
            "scope":contract["scope"]}
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    args.report_output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()
