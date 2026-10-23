"""Exercise the browser route with actual verified model weights, never a double."""
import html
import json
from pathlib import Path
import re

from wsgi import app

with app.test_client() as client:
    assert client.get("/healthz").status_code == 200
    assert client.get("/").status_code == 200
    with client.session_transaction() as state:
        token = state["csrf"]
    response = client.post("/review", data={"csrf": token, "mode": "demo"})
    if response.status_code != 200:
        raise RuntimeError("Real-model browser route failed: " + str(response.status_code))
    payload = re.search(r'<textarea id="report-json" hidden>(.*?)</textarea>', response.get_data(as_text=True), re.S)
    if payload is None:
        raise RuntimeError("Expected downloadable review report")
    report = json.loads(html.unescape(payload.group(1)))
    if report["model_calls"] < 1 or report["passages_omitted"] != 0 or report["status"] != "REVIEW_REQUIRED":
        raise RuntimeError("Actual inference or preservation contract failed")
    result = {"route_status": response.status_code, "test_double": False,
              **{key: report[key] for key in ("model", "model_calls", "passage_count", "passages_omitted", "processing_seconds", "status")}}
    Path("runner-web-result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
