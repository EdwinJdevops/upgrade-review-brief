"""Exercise real hosted inference plus inventory, using only sanitized fixtures.

The deployment revision is verified separately through Render, not trusted from
an operator-provided --commit argument alone. No browser certificate bypass.
"""
import argparse
from datetime import datetime, timezone
import html
import http.cookiejar
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request
import uuid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="https://upgrade-review-brief.onrender.com")
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    with opener.open(base + "/healthz", timeout=30) as response:
        assert response.status == 200 and json.load(response) == {"status": "ready"}

    def token():
        with opener.open(base + "/", timeout=30) as response:
            page = response.read().decode()
        return html.unescape(re.search(r'name="csrf" value="([^"]+)"', page)[1])

    def read_report(request):
        with opener.open(request, timeout=120) as response:
            assert response.status == 200
            body = response.read().decode()
        report = json.loads(html.unescape(re.search(r'<textarea id="report-json" hidden>(.*?)</textarea>', body, re.S)[1]))
        assert report["status"] == "REVIEW_REQUIRED" and report["model_calls"] > 0
        assert report["model"]["name"] == "BAAI/bge-reranker-base"
        assert report["generated_actions"] == [] and report["live_identity_verified"] is False
        assert "Changes outside this review." in body
        assert "Manifest coverage inventory" in body
        return report, body

    request = urllib.request.Request(base + "/review", data=urllib.parse.urlencode(
        {"csrf": token(), "mode": "demo_range"}).encode(), method="POST")
    ranged, _ = read_report(request)
    assert ranged["input_provenance"] == "packaged_demo"
    assert ranged["model_calls"] == 32 and ranged["passage_count"] == 16
    assert len(ranged["reading_tasks"]) == 2
    assert ranged["coverage"]["unscored_query_passage_pairs"] == 0
    inv = ranged["manifest_inventory"]
    assert inv["before_resource_count"] == inv["after_resource_count"] == 3
    assert inv["outside_scope_changed_resources"] == 3
    assert inv["metadata_only_modified_resources"] == 2
    assert {r["kind"] for r in inv["resources"]} == {"Deployment", "Service", "ServiceAccount"}
    commit = "b39300d09d6d70297dc437015d4a49e484b7b77d"
    assert ranged["source_reference"]["commit"] == commit
    assert ranged["source_reference"]["remote_content_verified_this_review"] is False
    assert all("/blob/" + commit + "/" in p["source_line_url"] and "#L" in p["source_line_url"] for p in ranged["source_passages"])
    original_request = urllib.request.Request(base + "/review", data=urllib.parse.urlencode(
        {"csrf": token(), "mode": "demo"}).encode(), method="POST")
    original, _ = read_report(original_request)
    assert original["model_calls"] == original["passage_count"] == 5
    assert original["source_reference"]["commit"] == commit
    assert all("/blob/" + commit + "/" in p["source_line_url"] and "#L" in p["source_line_url"] for p in original["source_passages"])

    root = Path(__file__).resolve().parents[1]
    # Fixture contains deliberate fake sentinels, never customer credentials.
    import sys
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / "tests"))
    from test_brief import BEFORE, AFTER
    secret = '\n---\napiVersion: v1\nkind: Secret\nmetadata:\n  name: example-credentials\ndata:\n  sensitive-key-sentinel: fake-old-sentinel\n'
    before = BEFORE + secret
    after = AFTER.replace("spec:\n  template:", "spec:\n  replicas: 0\n  template:") + secret.replace("fake-old-sentinel", "fake-new-sentinel")
    fields = {"csrf": token(), "mode": "upload", "deployment": "gateway", "namespace": "lab",
              "source_url": "https://example.org/controlled-guide", "section": "release"}
    files = {"before": ("before.yaml", before), "after": ("after.yaml", after),
             "notes": ("guide.md", "## release\nCheck the migration prerequisites for readiness changes.\n\nRead the full source before deciding.\n")}
    boundary = "review-" + uuid.uuid4().hex
    parts = []
    for name, value in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    for name, (filename, value) in files.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{filename}"\r\nContent-Type: text/plain\r\n\r\n{value}\r\n'.encode())
    parts.append(f"--{boundary}--\r\n".encode())
    request = urllib.request.Request(base + "/review", data=b"".join(parts), method="POST",
                                     headers={"Content-Type": "multipart/form-data; boundary=" + boundary})
    uploaded, body = read_report(request)
    assert uploaded["input_provenance"] == "user_supplied_bytes_not_authenticated"
    assert uploaded["source_reference"]["reference_type"] == "immutable_reference_not_established"
    assert uploaded["source_reference"]["remote_content_verified_this_review"] is False
    assert uploaded["manifest_inventory"]["outside_scope_changed_resources"] == 2
    assert len(uploaded["changes"]) == 1  # replicas and Secret were not model-reviewed
    for private in ("sensitive-key-sentinel", "fake-old-sentinel", "fake-new-sentinel", "do-not-send-this-value", "private-header", "PRIVATE_TOKEN"):
        assert private not in body
    assert "deployment settings" in body and "Separate review needed" in body
    out = {"checked_at": datetime.now(timezone.utc).isoformat(), "url": base,
           "expected_commit_verified_separately_by_render": args.commit,
           "system_tls_validation": True, "health_status": 200,
           "range": {"model": ranged["model"], "model_windows": ranged["model_calls"],
                     "passages": ranged["passage_count"], "outside_scope_resources": inv["outside_scope_changed_resources"],
                     "resource_kinds": [r["kind"] for r in inv["resources"]], "processing_seconds": ranged["processing_seconds"]},
           "pinned_source_links": {"commit": commit, "original_and_range_line_anchors_checked": True,
                                   "remote_content_verification_not_claimed_by_review": True},
           "metadata_only_modified_resources": inv["metadata_only_modified_resources"],
           "sanitized_upload": {"model_windows": uploaded["model_calls"], "focused_changes": len(uploaded["changes"]),
                                "outside_scope_resources": 2, "secret_sentinels_absent_from_response": True,
                                "processing_seconds": uploaded["processing_seconds"]},
           "boundary": "Actual model execution and HTTP/export checks; not relevance accuracy, engineer benefit, Kubernetes semantic validation or production capacity."}
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
