"""Prepare a local/CI review directly from three files; no case JSON is required."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import yaml

from upgrade_brief import build_brief, markdown, snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("before", "after", "guide"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--deployment", required=True)
    parser.add_argument("--namespace", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--section", help="Explicit heading; default selects stable release range plus unversioned context")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--model-dir", type=Path)
    group.add_argument("--lexical-baseline", action="store_true")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--fail-on-unreviewed-changes", action="store_true",
                        help="Emit the report, then exit 3 if manifest edits exist outside the focused scope. Exit 0 never means approval.")
    args = parser.parse_args()
    try:
        selector = {"name": args.deployment, "namespace": args.namespace}
        case = {"schema_version": 1, "deployment": selector}
        with tempfile.TemporaryDirectory(prefix="upgrade-review-cli-") as temp:
            root = Path(temp)
            for key, source, filename, limit in (("before", args.before, "before.yaml", 128*1024),
                                                ("after", args.after, "after.yaml", 128*1024),
                                                ("notes", args.guide, "guide.md", 64*1024)):
                with source.open("rb") as f:
                    data = f.read(limit + 1)
                if not data or len(data) > limit:
                    raise ValueError("Input is empty or exceeds supported size")
                (root / filename).write_bytes(data)
                case[key] = {"path": filename, "sha256": hashlib.sha256(data).hexdigest()}
                if key != "notes":
                    case["from_chart" if key == "before" else "to_chart"] = snapshot(data.decode("utf-8"), selector)["chart_label"]
            case["notes"].update(url=args.source_url)
            if args.section:
                case["notes"]["section"] = args.section
            else:
                case["notes"]["selection"] = "version_range"
            build_brief(case, root)
            scorer = None
            if args.model_dir:
                from rank_model import LocalReranker, MODEL, REVISION
                scorer = LocalReranker(args.model_dir)
            report = build_brief(case, root, scorer)
            if scorer:
                report["model"] = {"name": MODEL, "revision": REVISION, "runtime": "local_cpu_float32"}
            print(json.dumps(report, indent=2) if args.format == "json" else markdown(report))
            if args.fail_on_unreviewed_changes and report["manifest_inventory"]["outside_scope_changed_resources"]:
                return 3
    except (OSError, ValueError, TypeError, KeyError, RecursionError, yaml.YAMLError):
        parser.exit(2, "Review failed: check input files, Deployment identity, chart versions and guide headings. No approval was produced.\n")


if __name__ == "__main__":
    raise SystemExit(main())
