"""Measure HTTP requests to the existing demo, preserving every attempted run."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import html
import http.cookiejar
import json
import math
from pathlib import Path
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request


def opener():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def fetch(client, request):
    started = time.perf_counter()
    try:
        with client.open(request, timeout=180) as response:
            body, status = response.read(), response.status
        error = None
    except urllib.error.HTTPError as exc:
        body, status, error = exc.read(), exc.code, None
    except (OSError, TimeoutError) as exc:
        body, status, error = b"", None, type(exc).__name__
    return {"status": status, "seconds": time.perf_counter() - started, "error": error}, body


def quantiles(values):
    values = sorted(values)
    return {"n": len(values), **{name: values[max(0, math.ceil(p * len(values)) - 1)] if values else None
                                for name, p in (("p50", .5), ("p95", .95))}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="https://upgrade-review-brief.onrender.com")
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--interval", type=float, default=12)
    args = parser.parse_args()
    if args.interval < 12:
        parser.error("Keep at least twelve seconds between serial review starts")
    out = args.output_directory
    out.mkdir(parents=True, exist_ok=True)
    raw = out / "requests.jsonl"
    if raw.exists():
        parser.error("Choose a new output directory; do not overwrite measurements")
    base = args.base_url.rstrip("/")
    health, body = fetch(opener(), base + "/healthz")
    observed = json.loads(body)
    (out / "health-before.json").write_text(json.dumps({**health, "body": observed}, indent=2) + "\n")
    if observed.get("git_sha") != args.expected_sha or health["status"] != 200:
        raise RuntimeError("Expected deployment is not healthy")
    records = []
    guard = threading.Lock()

    def record(item, body):
        item["response_sha256"] = hashlib.sha256(body).hexdigest()
        item["observed_at_utc"] = datetime.now(timezone.utc).isoformat()
        text = body.decode("utf-8", errors="replace")
        report = re.search(r'<textarea id="report-json" hidden>(.*?)</textarea>', text, re.S)
        if report:
            report_value = json.loads(html.unescape(report[1]))
            (out / (item["id"] + ".report.json")).write_text(json.dumps(report_value, indent=2) + "\n")
            item["model_windows"] = report_value.get("model_calls")
        elif item["kind"] != "homepage":
            (out / (item["id"] + ".response.html")).write_bytes(body)
            item["visible_message"] = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text)).split())[:1000]
        with guard:
            records.append(item)
            with raw.open("a") as stream:
                stream.write(json.dumps(item) + "\n")
        print(json.dumps(item), flush=True)

    def prepared_client():
        client = opener()
        get, body = fetch(client, base + "/")
        if get["status"] != 200:
            raise RuntimeError("Could not prepare review form")
        match = re.search(r'name="csrf" value="([^"]+)"', body.decode())
        if not match:
            raise RuntimeError("Review form has no CSRF token")
        return client, html.unescape(match[1]), get["seconds"]

    def review(identifier, mode, prepared=None, barrier=None):
        started = time.perf_counter()
        client, token, form_seconds = prepared or prepared_client()
        if barrier:
            barrier.wait(timeout=30)
            started = time.perf_counter()
        request = urllib.request.Request(base + "/review", method="POST",
                    data=urllib.parse.urlencode({"csrf": token, "mode": mode}).encode())
        result, body = fetch(client, request)
        record({"id": identifier, "kind": mode, "form_get_seconds": form_seconds,
                "post_seconds": result.pop("seconds"), "end_to_end_seconds": time.perf_counter() - started,
                "concurrent_prepared_form": prepared is not None, **result}, body)

    for number in range(10):
        result, body = fetch(opener(), base + "/")
        record({"id": f"warm-home-{number+1:02}", "kind": "homepage", **result}, body)
    previous_start = None
    for mode, count in (("demo", 20), ("demo_range", 10)):
        for number in range(count):
            if previous_start is not None:
                while time.monotonic() - previous_start < args.interval:
                    time.sleep(min(1, args.interval - (time.monotonic() - previous_start)))
            previous_start = time.monotonic()
            review(f"{mode}-{number+1:02}", mode)
    # Leave a full rate-limit window before each independent concurrency burst.
    for count in (2, 5):
        for _ in range(62):
            time.sleep(1)
        clients = [prepared_client() for _ in range(count)]
        barrier = threading.Barrier(count)
        with ThreadPoolExecutor(max_workers=count) as pool:
            futures = [pool.submit(review, f"concurrent-{count}-{i+1}", "demo_range", clients[i], barrier) for i in range(count)]
            for future in futures:
                future.result()
    health, body = fetch(opener(), base + "/healthz")
    ending_health = json.loads(body)
    (out / "health-after.json").write_text(json.dumps({**health, "body": ending_health}, indent=2) + "\n")
    summary = {"expected_sha": args.expected_sha, "ending_sha_match": ending_health.get("git_sha") == args.expected_sha,
               "percentile_method": "nearest rank; successful serial requests only; all failures remain in requests.jsonl",
               "cold_start": "NOT RUN: restarting the service is not available through the connected API and dashboard sign-in is required",
               "serial": {}, "concurrent": {}}
    for kind in ("demo", "demo_range"):
        selected = [r for r in records if r["kind"] == kind and not r["id"].startswith("concurrent")]
        good = [r for r in selected if r["status"] == 200]
        summary["serial"][kind] = {"attempts": len(selected), "failures": [r["id"] for r in selected if r["status"] != 200],
                "form_get_plus_review_post_seconds": quantiles([r["end_to_end_seconds"] for r in good]),
                "post_seconds": quantiles([r["post_seconds"] for r in good])}
    summary["warm_homepage_seconds"] = quantiles([r["seconds"] for r in records if r["kind"] == "homepage" and r["status"] == 200])
    for count in (2, 5):
        summary["concurrent"][str(count)] = [r for r in records if r["id"].startswith(f"concurrent-{count}-")]
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
