"""Browser boundary tests. Scorer doubles do not establish model quality."""
import html
import hashlib
import io
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from test_brief import BEFORE, AFTER
from rank_model import LocalReranker
from webapp import create_app, RequestScorer


class ScorerDouble:
    def __init__(self):
        self.calls = []

    def score(self, query, passage, window_limit=32):
        self.calls.append((query, passage, window_limit))
        if window_limit <= 0:
            return {"score": None, "model_executed": False, "window_count": 0, "reason": "request_window_budget_exhausted"}
        return {"score": 0.25, "model_executed": True, "window_count": 1, "reason": "test_double"}


class WebTests(unittest.TestCase):
    def setUp(self):
        self.scorer = ScorerDouble()
        self.app = create_app(self.scorer, {"TESTING": True, "SECRET_KEY": "test-key"})
        self.client = self.app.test_client()
        self.client.get("/")
        with self.client.session_transaction() as state:
            self.csrf = state["csrf"]

    def data(self, notes="## release\nReadiness changes require review.\n\nOther guidance."):
        return {"csrf": self.csrf, "mode": "upload", "deployment": "gateway", "namespace": "lab",
                "source_url": "https://example.org/migration", "section": "release",
                "before": (io.BytesIO(BEFORE.encode()), "../../before.yaml"),
                "after": (io.BytesIO(AFTER.encode()), "after.yaml"),
                "notes": (io.BytesIO(notes.encode()), "guide.md")}

    def report(self, response):
        text = response.get_data(as_text=True)
        raw = re.search(r'<textarea id="report-json" hidden>(.*?)</textarea>', text, re.S).group(1)
        return json.loads(html.unescape(raw))

    def test_success_preserves_boundaries_and_cleans_uploads(self):
        with tempfile.TemporaryDirectory() as parent:
            actual = tempfile.TemporaryDirectory
            def temporary(**kwargs):
                return actual(dir=parent, **kwargs)
            with patch("webapp.tempfile.TemporaryDirectory", side_effect=temporary):
                response = self.client.post("/review", data=self.data())
            self.assertEqual(list(Path(parent).iterdir()), [])
        self.assertEqual(response.status_code, 200)
        report = self.report(response)
        self.assertEqual(report["model_calls"], 2)
        self.assertEqual(report["passages_omitted"], 0)
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        self.assertEqual(report["generated_actions"], [])
        for item in self.scorer.calls:
            self.assertNotIn("do-not-send-this-value", item[0])
            self.assertNotIn("private-header", item[0])
        self.assertNotIn("do-not-send-this-value", response.get_data(as_text=True))
        self.assertEqual(report["input_identities"]["before"]["path"], "before.yaml")

    def test_missing_or_unicode_csrf_rejected(self):
        for csrf in ("", "wrong", "\u2603"):
            data = self.data()
            data["csrf"] = csrf
            self.assertEqual(self.client.post("/review", data=data).status_code, 403)
        self.assertEqual(self.scorer.calls, [])

    def test_blank_section_selects_version_range_and_emits_reading_coverage(self):
        data = self.data("## General notes\nCheck prerequisites.\n## 2.26.0\nReadiness changes.\n## 2.27.0\nFuture material.")
        data["section"] = ""
        response = self.client.post("/review", data=data)
        self.assertEqual(response.status_code,200)
        report = self.report(response)
        self.assertEqual(report["coverage"]["mode"],"version_range")
        self.assertEqual({p["section"] for p in report["source_passages"]},{"General notes","2.26.0"})
        self.assertEqual(len(report["reading_tasks"]),1)
        self.assertFalse(report["coverage"]["version_history_complete_verified"])

    def test_range_demo_uses_two_actual_render_changes(self):
        # Network-free test: real committed renders, synthetic guide and scorer.
        from webapp import ROOT
        case=json.loads((ROOT/"brief-cases/kong-range.json").read_text())
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for key in ("before","after"):
                dest=root/case[key]["path"]
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes((ROOT/case[key]["path"]).read_bytes())
            guide="## General notes\nGeneral prerequisites.\n## 2.19.0\nFilesystem conditions.\n## 2.26.0\nHealth conditions.\n"
            dest=root/case["notes"]["path"]
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_text(guide)
            case["notes"]["sha256"]=hashlib.sha256(guide.encode()).hexdigest()
            (root/"brief-cases").mkdir()
            (root/"brief-cases/kong-range.json").write_text(json.dumps(case))
            with patch("webapp.ROOT",root):
                response = self.client.post("/review",data={"csrf":self.csrf,"mode":"demo_range"})
        self.assertEqual(response.status_code,200)
        report = self.report(response)
        self.assertEqual(report["from_chart"],"kong-2.18.0")
        self.assertEqual(report["to_chart"],"kong-2.26.0")
        self.assertEqual(len(report["changes"]),2)
        self.assertEqual(report["model_calls"],6)
        self.assertEqual(report["coverage"]["unscored_query_passage_pairs"],0)
        self.assertEqual(report["status"],"REVIEW_REQUIRED")

    def test_alias_yaml_rejected_before_inference(self):
        data = self.data()
        data["before"] = (io.BytesIO(b"x: &x [a]\ny: *x"), "before.yaml")
        self.assertEqual(self.client.post("/review", data=data).status_code, 400)
        self.assertEqual(self.scorer.calls, [])

    def test_invalid_source_url_not_rendered_or_fetched(self):
        for url in ("javascript:alert(1)", "https://name:secret@example.org/file"):
            data = self.data()
            data["source_url"] = url
            response = self.client.post("/review", data=data)
            self.assertEqual(response.status_code, 400)
            self.assertNotIn(url, response.get_data(as_text=True))
        self.assertEqual(self.scorer.calls, [])

    def test_untrusted_source_markup_is_escaped(self):
        response = self.client.post("/review", data=self.data("## release\n<script>alert(1)</script>\n"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("<script>alert(1)</script>", response.get_data(as_text=True))
        self.assertIn("&lt;script&gt;", response.get_data(as_text=True))

    def test_file_and_request_size_limits(self):
        data = self.data()
        data["notes"] = (io.BytesIO(b"x" * (64 * 1024 + 1)), "guide.md")
        self.assertEqual(self.client.post("/review", data=data).status_code, 400)
        response = self.client.post("/review", data=b"x" * (384 * 1024 + 1), content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, 413)
        self.assertEqual(self.scorer.calls, [])

    def test_guide_larger_than_parser_chunk_is_accepted_within_file_limit(self):
        notes = "## release\nReadiness requires review.\n## unselected\n" + "x" * 35000
        response = self.client.post("/review", data=self.data(notes))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.report(response)["passage_count"], 1)

    def test_model_unavailable_does_not_return_baseline(self):
        self.app.extensions["review_scorer"] = None
        self.assertEqual(self.client.get("/healthz").status_code, 503)
        response = self.client.post("/review", data=self.data())
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('id="report-json"', response.get_data(as_text=True))

    def test_model_failure_releases_lock_and_cleans_files(self):
        with patch.object(self.scorer, "score", side_effect=RuntimeError("private material")):
            response = self.client.post("/review", data=self.data())
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private material", response.get_data(as_text=True))
        self.assertFalse(self.app.extensions["review_lock"].locked())

    def test_concurrency_and_rate_limit(self):
        lock = self.app.extensions["review_lock"]
        lock.acquire()
        try:
            self.assertEqual(self.client.post("/review", data=self.data()).status_code, 429)
        finally:
            lock.release()
        self.app.config["REVIEW_LIMIT_PER_MINUTE"] = 1
        self.assertEqual(self.client.post("/review", data=self.data()).status_code, 200)
        self.assertEqual(self.client.post("/review", data=self.data()).status_code, 429)

    def test_security_headers_and_ready_health(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("frame-ancestors 'none'", response.headers["Content-Security-Policy"])
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(self.client.get("/healthz").json, {"status": "ready"})

    def test_request_window_budget_and_core_zero_window_guard(self):
        bounded = RequestScorer(self.scorer)
        for _ in range(35):
            bounded.score("query", "passage")
        self.assertEqual(bounded.remaining, 0)
        result = object.__new__(LocalReranker).score("query", "passage", window_limit=0)
        self.assertFalse(result["model_executed"])
        self.assertEqual(result["reason"], "request_window_budget_exhausted")


if __name__ == "__main__":
    unittest.main()
