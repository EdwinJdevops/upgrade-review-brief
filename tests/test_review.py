"""Acceptance checks for abstention and documentation-rule boundary behavior.

All facts are synthetic. These are not model accuracy or Helm runtime tests.
"""
import copy
import json
import unittest
from pathlib import Path

from upgrade_review import evaluate

ROOT = Path(__file__).resolve().parents[1]


class EvidenceContract(unittest.TestCase):
    def setUp(self):
        self.snapshot = json.loads((ROOT / "examples/affected.json").read_text())

    def result(self):
        report = evaluate(self.snapshot)
        return report["applicability"], report["satisfaction"]

    def test_documented_affected_combination_is_flagged(self):
        self.assertEqual(self.result(), ("APPLIES", "CONTRADICTS_SUPPLIED_FACTS"))

    def test_missing_external_controller_never_becomes_satisfied(self):
        del self.snapshot["facts"]["controller_version"]
        self.assertEqual(self.result(), ("UNKNOWN", "UNKNOWN"))
        self.assertIn("controller_version", evaluate(self.snapshot)["missing_evidence"])

    def test_adding_controller_evidence_resolves_only_applicability(self):
        before = copy.deepcopy(self.snapshot)
        del before["facts"]["controller_version"]
        self.assertEqual(evaluate(before)["applicability"], "UNKNOWN")
        self.assertEqual(self.result(), ("APPLIES", "CONTRADICTS_SUPPLIED_FACTS"))

    def test_explicit_remedy_only_satisfies_this_configuration_check(self):
        self.snapshot["facts"]["target_readiness_path"]["value"] = "/status"
        self.assertEqual(self.result(), ("APPLIES", "MATCHES_SUPPLIED_FACTS"))
        self.assertIn("unverified", evaluate(self.snapshot)["limitation"])

    def test_newer_controller_excludes_this_condition(self):
        self.snapshot["facts"]["controller_version"]["value"] = "2.11.0"
        self.assertEqual(self.result(), ("NOT_APPLICABLE", "UNKNOWN"))

    def test_known_false_condition_does_not_require_unrelated_facts(self):
        self.snapshot["facts"] = {
            "separate_deployments": {"value": False, "reference": "synthetic/layout"}
        }
        self.assertEqual(self.result(), ("NOT_APPLICABLE", "UNKNOWN"))

    def test_readiness_is_not_inferred_when_missing(self):
        del self.snapshot["facts"]["target_readiness_path"]
        self.assertEqual(self.result(), ("APPLIES", "UNKNOWN"))

    def test_unsupported_transition_does_not_look_covered(self):
        for old, new in [("2.24.0", "2.25.0"), ("2.26.0", "2.27.0"),
                         ("2.26.0", "2.26.0"), ("2.27.0", "2.26.0")]:
            with self.subTest(old=old, new=new):
                self.snapshot.update(from_version=old, to_version=new)
                self.assertEqual(self.result(), ("UNKNOWN", "UNKNOWN"))

    def test_ambiguous_controller_tags_are_unknown(self):
        for tag in ("latest", "2.10", "2.11.0-rc.1", "image@sha256:abc", None, True):
            with self.subTest(tag=tag):
                self.snapshot["facts"]["controller_version"]["value"] = tag
                self.assertEqual(self.result(), ("UNKNOWN", "UNKNOWN"))

    def test_boundary_patches_follow_documented_minor_version_condition(self):
        self.snapshot["facts"]["controller_version"]["value"] = "2.10.99"
        self.snapshot["facts"]["proxy_version"]["value"] = "3.3.99"
        self.assertEqual(self.result(), ("APPLIES", "CONTRADICTS_SUPPLIED_FACTS"))

    def test_references_are_required_and_boolean_strings_are_not_facts(self):
        self.snapshot["facts"]["controller_version"]["reference"] = " "
        self.assertEqual(self.result(), ("UNKNOWN", "UNKNOWN"))
        self.setUp()
        self.snapshot["facts"]["separate_deployments"]["value"] = "false"
        self.assertEqual(self.result(), ("UNKNOWN", "UNKNOWN"))

    def test_unknown_endpoint_is_not_an_assumed_remedy(self):
        self.snapshot["facts"]["target_readiness_path"]["value"] = "/custom-health"
        self.assertEqual(self.result(), ("APPLIES", "UNKNOWN"))

    def test_other_chart_is_explicitly_uncovered(self):
        self.snapshot["chart"] = "other/kong"
        self.assertEqual(self.result(), ("UNKNOWN", "UNKNOWN"))

    def test_malformed_top_level_is_rejected(self):
        for data in ([], None, {"facts": []}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                evaluate(data)


if __name__ == "__main__":
    unittest.main()
