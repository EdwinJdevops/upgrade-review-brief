"""Stable citations are useful, but never authenticate supplied guide bytes."""
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import base64
import io
import tempfile

from source_reference import describe_source
import prepare_brief_source

COMMIT = "b39300d09d6d70297dc437015d4a49e484b7b77d"
URL = "https://github.com/Kong/charts/blob/" + COMMIT + "/charts/kong/UPGRADE.md"


class ReferenceTests(unittest.TestCase):
    def test_full_commit_is_recorded_without_claiming_remote_verification(self):
        report = describe_source(URL + "#L89-L97")
        self.assertEqual(report["reference_type"], "github_commit")
        self.assertEqual(report["commit"], COMMIT)
        self.assertFalse(report["remote_content_verified_this_review"])

    def test_branch_tag_short_revision_and_other_hosts_do_not_gain_trust(self):
        for url in (URL.replace(COMMIT,"main"), URL.replace(COMMIT,"v2.26.0"), URL.replace(COMMIT,COMMIT[:7]),
                    URL.replace("github.com","github.com.example.org"), URL.replace("https:","http:"),
                    URL + "?raw=1", URL.replace("github.com","github.com:443"),
                    URL.replace("github.com","user@github.com")):
            with self.subTest(url=url):
                self.assertEqual(describe_source(url)["reference_type"], "immutable_reference_not_established")
                self.assertFalse(describe_source(url)["remote_content_verified_this_review"])

    def test_traversal_does_not_gain_commit_reference_status(self):
        self.assertIsNone(describe_source(URL + "/../other.md")["commit"])

    def test_demo_links_bind_to_recorded_publisher_commit_without_rewriting_frozen_experiment(self):
        root = Path(__file__).resolve().parents[1]
        for name in ("kong-range", "kong-readiness"):
            case = json.loads((root / "brief-cases" / (name + ".json")).read_text())
            self.assertTrue(case["notes"]["url"].startswith(URL))
            self.assertEqual(case["notes"]["sha256"], "327a5710b6d529d1b24e1200d8eaf60bf50a478a0ecf541b227e92394091248d")
        frozen = (root / "verification/range-evaluation-contract.json").read_bytes()
        self.assertEqual(hashlib.sha256(frozen).hexdigest(), "dbd485eaa030450baca072fbc5945f6d3767568e126651274c12c7df9a25f9c9")

    def test_preparation_binds_commit_path_response_blob_and_downloaded_bytes(self):
        data = b"# A synthetic guide\n"
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        payload = json.dumps({"sha": blob, "content": base64.b64encode(data).decode()}).encode()
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(prepare_brief_source, "__file__", str(Path(temp)/"prepare.py")), \
                 patch.object(prepare_brief_source, "BLOB", blob), \
                 patch.object(prepare_brief_source, "SHA256", hashlib.sha256(data).hexdigest()), \
                 patch("prepare_brief_source.urllib.request.urlopen", return_value=io.BytesIO(payload)) as fetch:
                prepare_brief_source.main()
                self.assertEqual(fetch.call_args.args[0], "https://api.github.com/repos/Kong/charts/contents/charts/kong/UPGRADE.md?ref=" + COMMIT)
                self.assertEqual((Path(temp)/"model-evaluation/sources/kong-guide.md").read_bytes(), data)

    def test_preparation_rejects_response_identity_before_writing_source(self):
        payload = json.dumps({"sha": "wrong", "content": base64.b64encode(b"wrong bytes").decode()}).encode()
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(prepare_brief_source, "__file__", str(Path(temp)/"prepare.py")), \
                 patch("prepare_brief_source.urllib.request.urlopen", return_value=io.BytesIO(payload)):
                with self.assertRaises(ValueError):
                    prepare_brief_source.main()
                self.assertFalse((Path(temp)/"model-evaluation/sources/kong-guide.md").exists())

    def test_preparation_rejects_modified_cached_source_without_network(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)/"model-evaluation/sources/kong-guide.md"
            target.parent.mkdir(parents=True)
            target.write_text("modified cache")
            with patch.object(prepare_brief_source, "__file__", str(Path(temp)/"prepare.py")), \
                 patch("prepare_brief_source.urllib.request.urlopen", side_effect=AssertionError("Unexpected network")):
                with self.assertRaises(ValueError):
                    prepare_brief_source.main()


if __name__ == "__main__":
    unittest.main()
