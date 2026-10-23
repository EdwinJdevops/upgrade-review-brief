"""Adversarial local-evidence tests. All controller manifests/bindings are fixtures."""
import copy
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import yaml

from review_artifacts import review

PROJECT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 20, 8, 30, tzinfo=timezone.utc)


class ArtifactContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = (PROJECT / "experiment/outputs/kong-new-proxy-only.yaml").read_bytes()
        self.case = {"chart": "kong/kong", "from_version": "2.25.0", "to_version": "2.26.0",
                     "proxy": {"name": "upgrade-review-kong", "namespace": "review"}}
        self.case["target"] = self.write("target.yaml", self.target)
        controller = {"apiVersion": "apps/v1", "kind": "Deployment",
                      "metadata": {"name": "external-controller", "namespace": "review"},
                      "spec": {"template": {"spec": {"containers": [{"name": "ingress-controller",
                          "image": "kong/kubernetes-ingress-controller:2.10.4"}]}}}}
        self.controller = controller

    def write(self, name, data):
        (self.root / name).write_bytes(data)
        return {"path": name, "sha256": hashlib.sha256(data).hexdigest(),
                "captured_at": "2026-10-20T08:00:00Z"}

    def external(self):
        self.case["controller"] = self.write("controller.yaml", yaml.safe_dump(self.controller).encode())
        binding = {"proxy": self.case["proxy"], "controller": {"name": "external-controller", "namespace": "review"}}
        self.case["binding"] = self.write("binding.json", json.dumps(binding).encode())

    def result(self):
        return review(self.case, self.root, now=NOW)

    def rejected(self):
        result = self.result()
        self.assertEqual((result["status"], result["applicability"], result["satisfaction"]),
                         ("EVIDENCE_REJECTED", "UNKNOWN", "UNKNOWN"))

    def test_actual_proxy_only_render_requires_external_facts(self):
        result = self.result()
        self.assertEqual(result["status"], "LOCAL_CONTENT_CHECKED")
        self.assertEqual(result["facts"]["target_readiness_path"]["value"], "/status/ready")
        self.assertEqual(result["applicability"], "UNKNOWN")
        self.assertIn("controller_version", result["missing_evidence"])

    def test_controller_fixture_plus_explicit_binding_flags_condition(self):
        self.external()
        result = self.result()
        self.assertEqual(result["applicability"], "APPLIES")
        self.assertEqual(result["satisfaction"], "CONTRADICTS_SUPPLIED_FACTS")
        self.assertFalse(result["live_identity_verified"])

    def test_remedy_matches_only_referenced_configuration(self):
        self.case["target"] = self.write("target.yaml", (PROJECT / "experiment/outputs/kong-new-override.yaml").read_bytes())
        self.external()
        result = self.result()
        self.assertEqual(result["satisfaction"], "MATCHES_SUPPLIED_FACTS")
        self.assertFalse(result["chart_render_binding_verified"])

    def test_unrelated_controller_without_binding_cannot_resolve_unknown(self):
        self.case["controller"] = self.write("controller.yaml", yaml.safe_dump(self.controller).encode())
        self.rejected()

    def test_binding_to_wrong_proxy_is_rejected(self):
        self.external()
        self.case["binding"] = self.write("binding.json", json.dumps({"proxy": {"name": "other", "namespace": "review"},
                            "controller": {"name": "external-controller", "namespace": "review"}}).encode())
        self.rejected()

    def test_tampered_target_is_rejected(self):
        (self.root / "target.yaml").write_bytes(self.target.replace(b"/status/ready", b"/status"))
        self.rejected()

    def test_recomputing_hash_does_not_authenticate_a_claim(self):
        self.case["target"] = self.write("target.yaml", self.target.replace(b"/status/ready", b"/status"))
        self.external()
        result = self.result()
        self.assertEqual(result["satisfaction"], "MATCHES_SUPPLIED_FACTS")
        self.assertFalse(result["live_identity_verified"])
        # Deliberately documents the remaining trust boundary, rather than claiming anti-forgery.

    def test_stale_and_future_timestamps_are_rejected(self):
        for ts in ("2026-10-18T08:00:00Z", "2026-10-21T08:00:00Z", "2026-10-20T08:00:00"):
            with self.subTest(ts=ts):
                self.case["target"]["captured_at"] = ts
                self.rejected()

    def test_stale_controller_cannot_supply_current_prerequisite(self):
        self.external()
        self.case["controller"]["captured_at"] = "2026-10-18T08:00:00Z"
        self.rejected()

    def test_namespace_scope_is_enforced(self):
        self.case["proxy"]["namespace"] = "other"
        self.rejected()

    def test_duplicate_matching_resources_are_rejected(self):
        self.case["target"] = self.write("target.yaml", self.target + b"\n" + self.target)
        self.rejected()

    def test_chart_label_conflict_is_rejected(self):
        self.case["to_version"] = "2.27.0"
        self.rejected()

    def test_traversal_and_external_symlink_are_rejected(self):
        self.case["target"]["path"] = "../target.yaml"
        self.rejected()
        (self.root / "escape.yaml").symlink_to(PROJECT / "experiment/outputs/kong-new-proxy-only.yaml")
        self.case["target"]["path"] = "escape.yaml"
        self.rejected()

    def test_duplicate_yaml_keys_and_aliases_are_rejected(self):
        for content in (b"kind: Deployment\nkind: Secret\n", b"a: &a [1]\nb: *a\n", b"!!python/object:os.system {}"):
            with self.subTest(content=content):
                self.case["target"] = self.write("target.yaml", content)
                self.rejected()

    def test_duplicate_json_binding_keys_are_rejected(self):
        self.external()
        self.case["binding"] = self.write("binding.json", b'{"proxy":{},"proxy":{}}')
        self.rejected()

    def test_unknown_repository_or_tag_cannot_supply_version(self):
        self.external()
        for image in ("other/controller:2.10.4", "kong/kubernetes-ingress-controller:latest",
                      "kong/kubernetes-ingress-controller@sha256:123"):
            with self.subTest(image=image):
                self.controller["spec"]["template"]["spec"]["containers"][0]["image"] = image
                self.case["controller"] = self.write("controller.yaml", yaml.safe_dump(self.controller).encode())
                result = self.result()
                self.assertEqual((result["applicability"], result["satisfaction"]), ("UNKNOWN", "UNKNOWN"))

    def test_colocated_render_is_not_a_separate_controller_case(self):
        self.case["target"] = self.write("target.yaml", (PROJECT / "experiment/outputs/kong-new-colocated-old-controller.yaml").read_bytes())
        self.assertEqual(self.result()["applicability"], "NOT_APPLICABLE")
        self.external()
        self.rejected()

    def test_oversized_and_excessively_nested_artifacts_are_rejected(self):
        for content in (b" " * 2_000_001, ("a: " * 42 + "1").encode()):
            self.case["target"] = self.write("target.yaml", content)
            self.rejected()


if __name__ == "__main__":
    unittest.main()
