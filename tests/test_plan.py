import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import yaml

from review_artifacts import EvidenceError
from review_plan import chart_version, select_range, source_line_url
from upgrade_brief import build_brief, markdown
from test_brief import BEFORE, AFTER

GUIDE = """# Guidance
## Table of contents
ignored
## General notes
General conditions must be checked.
## 2.27.0
Future behavior.
## 2.26.0
Readiness requires a separately managed component.

```yaml
## 2.99.0
path: /status
```
## 2.19.0
Plugins that write files need a writable location.
## 2.18.0
Already crossed this boundary.
"""


class CountingScorer:
    def __init__(self, windows=1):
        self.calls = []
        self.windows = windows

    def score(self, query, passage, window_limit=32):
        self.calls.append((query, passage, window_limit))
        if window_limit < self.windows:
            return {"score": None, "model_executed": False, "window_count": 0, "reason": "insufficient_budget"}
        return {"score": len(passage), "model_executed": True, "window_count": self.windows, "reason": "test_double"}


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        def put(name, text):
            (self.root / name).write_text(text)
            return {"path": name, "sha256": hashlib.sha256(text.encode()).hexdigest()}
        before = BEFORE.replace("kong-2.25.0", "kong-2.18.0")
        after = AFTER.replace("image: kong:3.3.0", "image: kong:3.3.0\n        securityContext:\n          readOnlyRootFilesystem: true")
        self.case = {"schema_version":1,"deployment":{"name":"gateway","namespace":"lab"},
                     "from_chart":"kong-2.18.0","to_chart":"kong-2.26.0",
                     "before":put("before.yaml",before),"after":put("after.yaml",after),
                     "notes":put("guide.md",GUIDE)|{"url":"https://example.org/guide","selection":"version_range"}}

    def test_range_includes_intermediate_and_general_excludes_endpoints_and_future(self):
        items, ledger = select_range(GUIDE, "kong-2.18.0", "kong-2.26.0")
        names = {p["section"] for p in items}
        self.assertEqual(names, {"General notes", "2.19.0", "2.26.0"})
        self.assertFalse(ledger["version_history_complete_verified"])
        self.assertEqual(ledger["sections"][0]["start_line"],1)
        self.assertNotIn("2.99.0", [s["heading"] for s in ledger["sections"]])
        joined = "\n".join(p["text"] for p in items)
        self.assertIn("separately managed", joined)
        self.assertIn("path: /status", joined)

    def test_stable_versions_numeric_not_lexicographic(self):
        text = "## 2.9.0\nOld.\n## 2.10.0\nNew.\n"
        items, _ = select_range(text, "chart-2.9.0", "chart-2.10.0")
        self.assertEqual([p["section"] for p in items], ["2.10.0"])
        for before, after in (("chart-2.0.0-rc.1","chart-2.1.0"),("chart-2.2.0","other-2.3.0"),("chart-2.2.0","chart-2.1.0"),("chart-2.2.0","chart-2.2.0")):
            with self.assertRaises(EvidenceError): select_range(text,before,after)
        self.assertEqual(chart_version("my-chart-2-1.2.3"), ("my-chart-2",(1,2,3)))

    def test_github_line_links_preserve_claimed_source_without_fetching(self):
        self.assertEqual(source_line_url("https://github.com/org/repo/blob/main/GUIDE.md#old",12,19),
                         "https://github.com/org/repo/blob/main/GUIDE.md#L12-L19")
        url="https://docs.example.org/migrate#release"
        self.assertEqual(source_line_url(url,12,19),url)
        url="https://github.com.example.org/org/repo/blob/main/GUIDE.md"
        self.assertEqual(source_line_url(url,12,19),url)

    def test_duplicate_headings_unmatched_fences_and_passage_limits_fail(self):
        for text in ("## 2.26.0\none\n## 2.26.0\ntwo", "## 2.26.0\n```\nunclosed", "## 2.26.0\n" + "text\n\n"*129):
            with self.assertRaises(EvidenceError): select_range(text,"kong-2.18.0","kong-2.26.0")

    def test_two_changes_get_separate_queries_and_exact_source_identities(self):
        scorer = CountingScorer()
        result = build_brief(self.case, self.root, scorer)
        self.assertEqual(len(result["reading_tasks"]), 2)
        self.assertEqual(result["passages_omitted"], 0)
        self.assertTrue(all(p["score"] is None for p in result["source_passages"]))
        self.assertTrue(all(t["unscored_passages"] == 0 for t in result["reading_tasks"]))
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertEqual(result["generated_actions"], [])
        self.assertFalse(result["live_identity_verified"])
        raw = json.dumps(result)
        self.assertNotIn("do-not-send-this-value", raw)
        self.assertNotIn("private-header", raw)
        for query, _, _ in scorer.calls:
            self.assertNotIn("PRIVATE_TOKEN", query)
        lines = GUIDE.splitlines(keepends=True)
        for p in result["source_passages"]:
            value = "".join(lines[p["start_line"]-1:p["end_line"]]).rstrip("\r\n")
            self.assertEqual(hashlib.sha256(value.encode()).hexdigest(),p["sha256"])
            self.assertIn(p["exact_excerpt"], value)
        self.assertLessEqual(sum(len(p["exact_excerpt"].split()) for p in result["source_passages"]),12)
        self.assertIn("Source selection ledger", markdown(result))

    def test_shared_budget_interleaves_fields_and_retains_unscored_material(self):
        source = "## 2.26.0\n" + "A distinct condition to review.\n\n"*20
        (self.root/"guide.md").write_text(source)
        self.case["notes"]["sha256"] = hashlib.sha256(source.encode()).hexdigest()
        scorer = CountingScorer(windows=2)
        result = build_brief(self.case,self.root,scorer)
        self.assertEqual(result["model_calls"],32)
        self.assertEqual(result["passage_count"],20)
        self.assertEqual(result["passages_omitted"],0)
        self.assertEqual([t["scored_passages"] for t in result["reading_tasks"]],[8,8])
        self.assertEqual(result["coverage"]["unscored_query_passage_pairs"],24)
        self.assertEqual(len(scorer.calls),16)

    def test_no_change_and_model_unavailable_never_produce_approval(self):
        # A chart-label-only change still warrants general prerequisite reading.
        data = (self.root/"before.yaml").read_text().replace("kong-2.18.0","kong-2.26.0")
        (self.root/"after.yaml").write_text(data)
        self.case["after"]["sha256"] = hashlib.sha256(data.encode()).hexdigest()
        report = build_brief(self.case,self.root)
        self.assertEqual(report["changes"],[])
        self.assertEqual(report["reading_tasks"][0]["field"],"general_prerequisites")
        self.assertEqual(report["model_calls"],0)
        self.assertEqual(report["status"],"REVIEW_REQUIRED")

    def test_changes_above_query_limit_remain_in_diff_and_coverage(self):
        old = yaml.safe_load((self.root/"before.yaml").read_text())
        new = copy.deepcopy(old)
        new["metadata"]["labels"]["helm.sh/chart"] = "kong-2.26.0"
        container = new["spec"]["template"]["spec"]["containers"][0]
        container["image"]="kong:3.4.0"
        container["securityContext"]={"readOnlyRootFilesystem":True}
        for name in ("readinessProbe","livenessProbe","startupProbe"):
            container[name]={"httpGet":{"path":"/changed","port":9090}}
        data=yaml.safe_dump(new)
        (self.root/"after.yaml").write_text(data)
        self.case["after"]["sha256"]=hashlib.sha256(data.encode()).hexdigest()
        report=build_brief(self.case,self.root,CountingScorer())
        self.assertEqual(len(report["changes"]),8)
        self.assertEqual(len(report["reading_tasks"]),6)
        self.assertEqual(len(report["coverage"]["changes_without_dedicated_query"]),2)
        self.assertEqual(report["passages_omitted"],0)


if __name__ == "__main__":
    unittest.main()
