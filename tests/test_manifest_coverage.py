"""Coverage boundaries and privacy, independently of source relevance/model scores."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

from manifest_coverage import inventory
from review_artifacts import EvidenceError
from upgrade_brief import build_brief, markdown, parse_manifests
from test_brief import BEFORE, AFTER


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.old = yaml.safe_load(BEFORE)
        self.new = yaml.safe_load(AFTER)

    def compare(self, before=None, after=None):
        return inventory([self.old] if before is None else before,
                         [self.new] if after is None else after, 0, 0)

    def test_known_probe_and_chart_label_change_does_not_claim_hidden_edits(self):
        report = self.compare()
        self.assertEqual(report["resource_changes"]["modified"], 1)
        self.assertEqual(report["outside_scope_changed_resources"], 0)

    def test_zero_focused_diff_can_still_hide_replica_change(self):
        self.new = copy.deepcopy(self.old)
        self.new["spec"]["replicas"] = 0
        report = self.compare()
        self.assertEqual(report["outside_scope_changed_resources"], 1)
        self.assertEqual(report["resources"][0]["unreviewed_categories"], ["deployment_settings"])

    def test_secret_change_added_service_removed_crd_and_unmodified_resource(self):
        def resource(kind, name, **body):
            return {"apiVersion": "v1", "kind": kind, "metadata": {"name": name}, **body}
        secret = resource("Secret", "credentials", data={"private-key-name": "old-sensitive-payload"})
        changed = copy.deepcopy(secret)
        changed["data"]["private-key-name"] = "new-sensitive-payload"
        crd = resource("CustomResourceDefinition", "widgets.example.org")
        account = resource("ServiceAccount", "worker")
        service = resource("Service", "proxy", spec={"ports": [{"port": 443}]})
        report = self.compare([self.old, secret, crd, account], [self.new, changed, account, service])
        self.assertEqual(report["outside_scope_changed_resources"], 3)
        self.assertEqual(report["resource_changes"], {"modified": 2, "added": 1, "removed": 1, "unchanged": 1})
        raw = json.dumps(report)
        for private in ("private-key-name", "old-sensitive-payload", "new-sensitive-payload", '"data"', '"ports"'):
            self.assertNotIn(private, raw)

    def test_unknown_keys_env_and_headers_are_detected_without_export(self):
        container = self.new["spec"]["template"]["spec"]["containers"][0]
        container["private-field-name"] = "private-value"
        container["env"][0]["value"] = "rotated-sensitive-token"
        container["readinessProbe"]["httpGet"]["httpHeaders"][0]["value"] = "rotated-header"
        report = self.compare()
        self.assertTrue(report["resources"][0]["outside_focused_scope"])
        for private in ("private-field-name", "private-value", "rotated-sensitive-token", "rotated-header", "Authorization"):
            self.assertNotIn(private, json.dumps(report))

    def test_init_container_and_volume_changes_are_not_model_reviewed(self):
        pod = self.new["spec"]["template"]["spec"]
        pod["initContainers"] = [{"name": "prepare", "image": "prepare:2", "args": ["sensitive-arg"]}]
        pod["volumes"] = [{"name": "data", "emptyDir": {}}]
        report = self.compare()
        self.assertIn("pod_settings_and_init_containers", report["resources"][0]["unreviewed_categories"])
        self.assertNotIn("sensitive-arg", json.dumps(report))

    def test_readonly_field_is_masked_but_other_security_changes_are_not(self):
        container = self.new["spec"]["template"]["spec"]["containers"][0]
        container["securityContext"] = {"readOnlyRootFilesystem": True}
        self.assertEqual(self.compare()["outside_scope_changed_resources"], 0)
        container["securityContext"]["privileged"] = True
        self.assertEqual(self.compare()["outside_scope_changed_resources"], 1)

    def test_probe_timing_and_exec_action_are_outside_scope(self):
        probe = self.new["spec"]["template"]["spec"]["containers"][0]["readinessProbe"]
        probe["periodSeconds"] = 5
        probe["exec"] = {"command": ["private-command"]}
        self.assertEqual(self.compare()["outside_scope_changed_resources"], 1)
        self.assertNotIn("private-command", json.dumps(self.compare()))

    def test_mapping_order_comments_and_resource_document_order_ignored(self):
        resource = {"apiVersion": "v1", "kind": "Service", "metadata": {"name": "a"}}
        reversed_keys = dict(reversed(list(resource.items())))
        report = inventory(parse_manifests(BEFORE + "\n# ignored comment\n---\n" + yaml.safe_dump(resource)),
                           [reversed_keys, self.old], 0, 1)
        self.assertEqual(report["resource_changes"]["unchanged"], 2)

    def test_omitted_namespace_is_not_assumed_equal_to_default(self):
        self.old["metadata"].pop("namespace")
        self.new["metadata"]["namespace"] = "default"
        report = self.compare()
        self.assertEqual(report["resource_changes"]["removed"], 1)
        self.assertEqual(report["resource_changes"]["added"], 1)
        self.assertEqual(report["outside_scope_changed_resources"], 2)
        self.assertIn(None, [r["namespace"] for r in report["resources"]])

    def test_api_version_change_is_visible_as_two_unreviewed_identities(self):
        self.new["apiVersion"] = "apps/v2"
        self.assertEqual(self.compare()["outside_scope_changed_resources"], 2)

    def test_duplicate_identity_and_unexpanded_lists_rejected(self):
        for docs in ([self.old, copy.deepcopy(self.old)], [self.old, {"apiVersion": "v1", "kind": "List", "items": []}],
                     [self.old, {"apiVersion": "v1", "kind": "PodList", "metadata": {"name": "named-wrapper"}, "items": []}]):
            with self.assertRaises(EvidenceError):
                self.compare(before=docs)

    def test_boolean_numeric_type_change_is_not_silently_equal(self):
        self.old["spec"]["unselected"] = True
        self.new["spec"]["unselected"] = 1
        self.assertEqual(self.compare()["outside_scope_changed_resources"], 1)

    def test_non_json_yaml_rejected_including_unselected_documents(self):
        for value in (float("nan"), float("inf"), {1: "value"}, yaml.safe_load("2026-10-23")):
            self.new["unselected"] = value
            with self.assertRaises(EvidenceError):
                self.compare()

    def test_build_rejects_ambiguous_inventory_before_model_execution(self):
        class MustNotRun:
            def score(self, *args, **kwargs):
                raise AssertionError("Invalid inventory reached inference")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            case = self.case_files(root, BEFORE + "\n---\napiVersion: v1\nkind: List\nitems: []\n", AFTER)
            with self.assertRaises(EvidenceError):
                build_brief(case, root, MustNotRun())

    @staticmethod
    def case_files(root, before, after):
        case = {"schema_version": 1, "deployment": {"name": "gateway", "namespace": "lab"},
                "from_chart": "kong-2.25.0", "to_chart": "kong-2.26.0"}
        for key, value, filename in (("before", before, "before.yaml"), ("after", after, "after.yaml"),
                                     ("notes", "## 2.26.0\nCheck migration prerequisites.\n", "guide.md")):
            (root / filename).write_text(value)
            case[key] = {"path": filename, "sha256": hashlib.sha256(value.encode()).hexdigest()}
        case["notes"].update(section="2.26.0", url="https://example.org/guide")
        return case

    def test_cli_guard_emits_report_and_distinct_exit_code_without_claiming_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.case_files(root, BEFORE, AFTER.replace("spec:\n  template:", "spec:\n  replicas: 0\n  template:"))
            command = [sys.executable, str(Path(__file__).resolve().parents[1] / "review_change.py"),
                       "--before", str(root / "before.yaml"), "--after", str(root / "after.yaml"),
                       "--guide", str(root / "guide.md"), "--deployment", "gateway", "--namespace", "lab",
                       "--source-url", "https://example.org/guide", "--lexical-baseline", "--format", "json"]
            result = subprocess.run(command + ["--fail-on-unreviewed-changes"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 3, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "REVIEW_REQUIRED")
            self.assertEqual(report["manifest_inventory"]["outside_scope_changed_resources"], 1)
            self.assertIn("deployment_settings", markdown(report))
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            (root / "after.yaml").write_text(AFTER)
            clean = subprocess.run(command + ["--fail-on-unreviewed-changes"], capture_output=True, text=True)
            self.assertEqual(clean.returncode, 0, clean.stderr)
            self.assertEqual(json.loads(clean.stdout)["status"], "REVIEW_REQUIRED")


if __name__ == "__main__":
    unittest.main()
