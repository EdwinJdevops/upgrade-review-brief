"""Bounded browser adapter for the same source-linked review engine."""
from collections import deque
import hashlib
import hmac
import json
import logging
import os
from pathlib import Path
import secrets
import tempfile
import threading
import time

from flask import Flask, jsonify, render_template, request, session
import yaml

from download_reranker import MODEL, REVISION
from review_artifacts import EvidenceError
from upgrade_brief import build_brief, markdown, snapshot

ROOT = Path(__file__).resolve().parent


class RequestScorer:
    """Share weights, but bound inference per request and retain unscored passages."""
    def __init__(self, model):
        self.model = model
        self.remaining = 32

    def score(self, query, passage, window_limit=32):
        result = self.model.score(query, passage, window_limit=min(self.remaining, window_limit))
        self.remaining -= result.get("window_count", 0)
        return result


def create_app(scorer=None, config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SESSION_SECRET") or secrets.token_hex(32),
        SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Strict",
        SESSION_COOKIE_SECURE=os.environ.get("RENDER") == "true",
        MAX_CONTENT_LENGTH=384 * 1024, MAX_FORM_MEMORY_SIZE=128 * 1024,
        MAX_FORM_PARTS=12, REVIEW_LIMIT_PER_MINUTE=6,
    )
    if config:
        app.config.update(config)
    app.extensions["review_scorer"] = scorer
    lock = threading.Lock()
    starts = deque()
    app.extensions["review_lock"] = lock

    @app.after_request
    def protect(response):
        response.headers.update({
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
            "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY",
            "Referrer-Policy": "no-referrer", "Cache-Control": "no-store",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        })
        return response

    @app.get("/healthz")
    def health():
        ready = app.extensions["review_scorer"] is not None
        return jsonify(
            status="ready" if ready else "model_unavailable",
            git_sha=os.environ.get("RENDER_GIT_COMMIT", "unknown"),
        ), 200 if ready else 503

    @app.get("/")
    def index():
        session.setdefault("csrf", secrets.token_urlsafe(32))
        return render_template("index.html", model_ready=app.extensions["review_scorer"] is not None)

    def fail(message, status):
        return render_template("error.html", message=message), status

    def field(name, limit=200):
        value = request.form.get(name, "").strip()
        if not value or len(value) > limit or any(ord(c) < 32 for c in value):
            raise EvidenceError("A valid " + name.replace("_", " ") + " is required")
        return value

    def uploaded_case(root):
        selector = {"name": field("deployment"), "namespace": field("namespace")}
        case = {"schema_version": 1, "deployment": selector}
        for key, filename, limit in (("before", "before.yaml", 128 * 1024),
                                     ("after", "after.yaml", 128 * 1024),
                                     ("notes", "notes.md", 64 * 1024)):
            upload = request.files.get(key)
            if upload is None:
                raise EvidenceError("Three input files are required")
            raw = upload.read(limit + 1)
            if not raw or len(raw) > limit:
                raise EvidenceError("Input file is empty or exceeds its size limit")
            text = raw.decode("utf-8")
            # Browser-supplied names never become server paths.
            (root / filename).write_bytes(raw)
            case[key] = {"path": filename, "sha256": hashlib.sha256(raw).hexdigest()}
            if key != "notes":
                case["from_chart" if key == "before" else "to_chart"] = snapshot(text, selector)["chart_label"]
        section = request.form.get("section", "").strip()
        if section:
            case["notes"].update(url=field("source_url", 2048), section=field("section"))
        else:
            case["notes"].update(url=field("source_url", 2048), selection="version_range")
        return case

    @app.post("/review")
    def review():
        supplied = request.form.get("csrf", "")
        expected = session.get("csrf", "")
        if not supplied or not expected or not hmac.compare_digest(supplied.encode(), expected.encode()):
            return fail("This form expired. Open the start page and try again.", 403)
        model = app.extensions["review_scorer"]
        if model is None:
            return fail("The open-weight model is unavailable. No substitute result was generated.", 503)
        if not lock.acquire(blocking=False):
            return fail("Another review is running. Try again when it finishes.", 429)
        try:
            now = time.monotonic()
            while starts and now - starts[0] >= 60:
                starts.popleft()
            if len(starts) >= app.config["REVIEW_LIMIT_PER_MINUTE"]:
                return fail("The demonstration has reached its review limit. Try again in one minute.", 429)
            starts.append(now)
            with tempfile.TemporaryDirectory(prefix="upgrade-review-") as temp:
                if request.form.get("mode") == "demo":
                    root = ROOT
                    case = json.loads((ROOT / "brief-cases/kong-readiness.json").read_text())
                elif request.form.get("mode") == "demo_range":
                    root = ROOT
                    case = json.loads((ROOT / "brief-cases/kong-range.json").read_text())
                elif request.form.get("mode") == "upload":
                    root = Path(temp)
                    case = uploaded_case(root)
                else:
                    raise EvidenceError("Choose the example or three-file review")
                # Complete validation before any model computation.
                build_brief(case, root)
                report = build_brief(case, root, RequestScorer(model))
                report["model"] = {"name": MODEL, "revision": REVISION, "runtime": "server_cpu_float32"}
                report["processing_seconds"] = round(time.monotonic() - now, 3)
                report["input_provenance"] = "packaged_demo" if request.form.get("mode") in ("demo", "demo_range") else "user_supplied_bytes_not_authenticated"
                if report["model_calls"] == 0:
                    return fail("No passage could be scored within the input limits. Shorten the selected material.", 422)
                # Retain neither uploaded bytes nor reports between requests.
                rendered = render_template("report.html", report=report, report_markdown=markdown(report))
            app.logger.info("review_complete passages=%d model_windows=%d elapsed_seconds=%.3f",
                            report["passage_count"], report["model_calls"], report["processing_seconds"])
            return rendered
        except (EvidenceError, UnicodeError, yaml.YAMLError, TypeError, KeyError, RecursionError):
            # Parser errors can contain source text. Never put them in logs or responses.
            return fail("Input validation failed. Check the Deployment selector, stable increasing Helm versions, UTF-8 files, HTTPS source URL and unique level-two guide headings. Resources need unique API-version/kind/namespace/name identities and JSON-compatible YAML; expand List wrappers first. For unsupported version formats, supply an explicit section.", 400)
        except (OSError, ValueError, RuntimeError):
            app.logger.error("review_failed operational_error")
            return fail("The review could not finish. No approval or substitute model result was generated.", 503)
        finally:
            lock.release()

    @app.errorhandler(413)
    def too_large(error):
        return fail("Request too large. Each manifest is limited to 128 KiB and the guide to 64 KiB.", 413)

    app.logger.setLevel(logging.INFO)
    return app
