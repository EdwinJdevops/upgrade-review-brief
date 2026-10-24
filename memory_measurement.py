"""RSS observations for the Linux Render process; never input/report content."""
from contextlib import contextmanager
import os
from pathlib import Path
import threading


def current_rss_bytes():
    try:
        return int(Path("/proc/self/statm").read_text().split()[1]) * os.sysconf("SC_PAGE_SIZE")
    except (OSError, ValueError, IndexError):
        return None


@contextmanager
def observe_inference_rss():
    stats = {"sampled_peak_rss_bytes": current_rss_bytes(), "sampling_interval_ms": 10}
    stopped = threading.Event()

    def sample():
        value = current_rss_bytes()
        if value is not None:
            stats["sampled_peak_rss_bytes"] = max(stats["sampled_peak_rss_bytes"] or 0, value)

    def monitor():
        while not stopped.wait(0.01):
            sample()

    thread = threading.Thread(target=monitor, daemon=True, name="inference-rss-observer")
    thread.start()
    try:
        yield stats
    finally:
        stopped.set()
        thread.join(timeout=1)
        sample()
        try:
            import resource
            stats["process_lifetime_peak_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        except ImportError:
            stats["process_lifetime_peak_rss_bytes"] = None
