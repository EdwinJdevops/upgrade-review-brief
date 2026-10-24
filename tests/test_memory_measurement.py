import threading
import unittest

from memory_measurement import current_rss_bytes, observe_inference_rss


class MemoryObservationTests(unittest.TestCase):
    def test_process_measurement_and_observer_cleanup(self):
        before = current_rss_bytes()
        self.assertIsInstance(before, int)
        self.assertGreater(before, 0)
        with observe_inference_rss() as stats:
            block = bytearray(1024 * 1024)
            block[-1] = 1
        self.assertGreater(stats["sampled_peak_rss_bytes"], 0)
        self.assertGreater(stats["process_lifetime_peak_rss_bytes"], 0)
        self.assertFalse(any(t.name == "inference-rss-observer" for t in threading.enumerate()))

    def test_observer_stops_if_review_raises(self):
        with self.assertRaises(ValueError):
            with observe_inference_rss():
                raise ValueError("controlled failure")
        self.assertFalse(any(t.name == "inference-rss-observer" for t in threading.enumerate()))
