import unittest

from verification.check_determinism import canonical_bytes


class DeterminismNormalizationTests(unittest.TestCase):
    def test_only_timing_metadata_removed(self):
        original = {"score": 0.123456, "passages": [{"id": "first", "inference_seconds": 1.2}], "checked_at": "today"}
        other_time = {"score": 0.123456, "passages": [{"id": "first", "inference_seconds": 9.9}], "checked_at": "later"}
        self.assertEqual(canonical_bytes(original), canonical_bytes(other_time))
        self.assertNotEqual(canonical_bytes(original), canonical_bytes({**original, "score": 0.123457}))
        self.assertNotEqual(canonical_bytes(original), canonical_bytes({**original, "passages": [{"id": "other"}]}))
