import copy
import hashlib
import tempfile
from pathlib import Path
import unittest

from review_artifacts import EvidenceError
from upgrade_brief import build_brief, markdown, note_passages, snapshot

BEFORE = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: gateway
  namespace: lab
  labels:
    helm.sh/chart: kong-2.25.0
spec:
  template:
    spec:
      containers:
      - name: proxy
        image: kong:3.3.0
        env:
        - name: PRIVATE_TOKEN
          value: do-not-send-this-value
        readinessProbe:
          httpGet:
            path: /status
            port: status
            httpHeaders:
            - name: Authorization
              value: private-header
"""
AFTER = BEFORE.replace("kong-2.25.0", "kong-2.26.0").replace("path: /status", "path: /status/ready")


class BriefTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        def put(name, content):
            (self.root / name).write_text(content)
            return {"path": name, "sha256": hashlib.sha256(content.encode()).hexdigest()}
        self.case = {"schema_version": 1, "deployment": {"name": "gateway", "namespace": "lab"},
                     "from_chart": "kong-2.25.0", "to_chart": "kong-2.26.0",
                     "before": put("before.yaml", BEFORE), "after": put("after.yaml", AFTER),
                     "notes": put("notes.md", "## 2.26.0\nFirst source paragraph about gateway health.\n\nSecond source paragraph.\n## 2.19.0\nUnselected material.\n") | {"url": "https://example.org/guide", "section": "2.26.0"}}

    def test_sensitive_unselected_fields_never_enter_query_or_report(self):
        result = build_brief(self.case, self.root)
        import json
        serialized = json.dumps(result)
        for secret in ("do-not-send-this-value", "private-header", "PRIVATE_TOKEN"):
            self.assertNotIn(secret, serialized)
        self.assertEqual(len(result["changes"]), 1)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertEqual(result["generated_actions"], [])

    def test_every_locator_and_excerpt_binds_to_source_bytes(self):
        result = build_brief(self.case, self.root)
        lines = (self.root / "notes.md").read_text().splitlines(keepends=True)
        for passage in result["source_passages"]:
            exact = "".join(lines[passage["start_line"]-1:passage["end_line"]]).rstrip("\r\n")
            self.assertEqual(hashlib.sha256(exact.encode()).hexdigest(), passage["sha256"])
            self.assertIn(passage["exact_excerpt"], exact)
        self.assertEqual(result["passages_omitted"], 0)
        self.assertEqual(result["passage_count"], 2)

    def test_model_unscored_passage_remains_visible(self):
        class TooLong:
            def score(self, query, passage):
                return {"score": None, "model_executed": False, "reason": "token_limit_no_silent_truncation"}
        result = build_brief(self.case, self.root, TooLong())
        self.assertEqual(len(result["source_passages"]), 2)
        self.assertEqual(result["model_calls"], 0)
        self.assertTrue(all(p["score"] is None for p in result["source_passages"]))

    def test_literal_preview_budget_follows_ranked_reading_order(self):
        class LaterFirst:
            def score(self, query, passage):
                return {"score": int(passage.startswith("Second")), "model_executed": True}
        report = build_brief(self.case, self.root, LaterFirst())
        self.assertTrue(report["source_passages"][0]["exact_excerpt"].startswith("Second"))
        self.assertLessEqual(sum(len(p["exact_excerpt"].split()) for p in report["source_passages"]), 12)

    def test_tampered_source_rejected(self):
        (self.root / "notes.md").write_text("edited")
        with self.assertRaises(EvidenceError):
            build_brief(self.case, self.root)

    def test_wrong_chart_declaration_rejected(self):
        self.case["to_chart"] = "kong-9.9.9"
        with self.assertRaises(EvidenceError):
            build_brief(self.case, self.root)

    def test_wrong_namespace_rejected(self):
        self.case["deployment"]["namespace"] = "production"
        with self.assertRaises(EvidenceError):
            build_brief(self.case, self.root)

    def test_aliases_and_duplicate_keys_rejected(self):
        for invalid in (BEFORE + "alias: &x [one]\ncopy: *x\n", BEFORE.replace("name: gateway", "name: gateway\n  name: other")):
            with self.assertRaises(EvidenceError):
                snapshot(invalid, self.case["deployment"])

    def test_duplicate_or_absent_section_rejected(self):
        for text in ("## other\nhello", "## 2.26.0\none\n## 2.26.0\ntwo"):
            with self.assertRaises(EvidenceError):
                note_passages(text, "2.26.0")

    def test_configuration_fence_stays_with_its_condition(self):
        text = "## release\nOnly when the extension writes files:\n\n```yaml\nreadOnlyRootFilesystem: false\n```\n\nOther material.\n"
        passages = note_passages(text, "release")
        self.assertEqual(len(passages), 2)
        self.assertIn("Only when", passages[0]["text"])
        self.assertIn("readOnlyRootFilesystem", passages[0]["text"])
        self.assertEqual(passages[0]["start_line"], 2)
        self.assertEqual(passages[0]["end_line"], 6)

    def test_no_change_never_becomes_approval(self):
        self.case["before"] = copy.deepcopy(self.case["after"])
        self.case["from_chart"] = self.case["to_chart"]
        result = build_brief(self.case, self.root)
        self.assertEqual(result["changes"], [])
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertFalse(result["live_identity_verified"])

    def test_path_escape_rejected(self):
        self.case["notes"]["path"] = "../notes.md"
        with self.assertRaises(EvidenceError):
            build_brief(self.case, self.root)

    def test_credential_or_script_source_url_rejected(self):
        for url in ("https://person:password@example.org/guide", "javascript:alert(1)", "https://example.org/\n[click](bad)"):
            self.case["notes"]["url"] = url
            with self.assertRaises(EvidenceError):
                build_brief(self.case, self.root)

    def test_source_markup_cannot_become_raw_html_or_markdown_link(self):
        source = "## 2.26.0\n<script>alert(1)</script> [link](javascript:alert(1))\n"
        (self.root / "notes.md").write_text(source)
        self.case["notes"]["sha256"] = hashlib.sha256(source.encode()).hexdigest()
        rendered = markdown(build_brief(self.case, self.root))
        self.assertNotIn("<script>", rendered)
        self.assertNotIn(" [link]", rendered)


if __name__ == "__main__":
    unittest.main()
