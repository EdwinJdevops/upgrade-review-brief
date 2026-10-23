# Deploy the browser review on Render

Status, October 23: **live at https://upgrade-review-brief.onrender.com**. The version-range feature was deployed on source commit `20487734b1a7d363de1d7e17176cb8a66a2c6df6`, and the final line-number correction on `8f518bd4c55eba69451cfc9a7bb8b2338acdec40` is live as deployment `dep-dbdmqloae00c738oama0`. The final revision passed 68 tests in GitHub Actions and a targeted system-TLS/inference check. Full public desktop/mobile checks for the feature revision covered the original example, uploads, exports, CSRF rejection and the 16-passage/32-window range review. See verification/render-range-release-2026-10-23.json for the exact revision/evidence split. Earlier deployment records are historical evidence and are retained.

Account billing was reviewed privately in the Dashboard; private balance and payment details are not published in this repository.

## Service definition

The live service was created directly through MCP, using the explicit commands, plan and non-secret environment values below. The checked-in `render.yaml` is the Blueprint specification for a future managed configuration; it is not currently synced to the service. To use it later, use **New → Blueprint** in Render and review how it will adopt the existing service before applying. The blueprint creates one Python web service; no database, persistent disk, GPU or background worker is requested.

- Build: `bash render-build.sh`
- Start: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 180 --no-control-socket --access-logfile -`
- Health endpoint: `/healthz`, ready only when the verified model has loaded. The live service was initially created with the default TCP probe. On October 23, `/healthz` was saved under Dashboard Settings → Health Checks and independently confirmed through the Render service API. See verification/render-health-monitoring-2026-10-23.json.
- Compute: `1c-2g` (1 CPU / 2 GB RAM in the current Blueprint reference).
- Automatic deployments: off. Deploy deliberately to avoid unnecessary repeated downloads/builds.
- Live session secret: generated in memory by Python `secrets` when the single worker starts; it is not persisted or exposed. Restarting expires open forms. A future Blueprint sync can instead generate `SESSION_SECRET` on Render. Never paste secret values into the repository, article or chat.

The previous local model experiment measured 1135.6 MiB peak process RSS. Render's 512 MB free compute is below that measurement. The 2 GB instance passed the included example and upload checks. A post-review sample reported 659,304,450 bytes (~629 MiB) against a 2 GiB limit. This is a sampled short run, not a measured peak or a load/capacity guarantee. Review current account credit and charges privately in the Dashboard; promotional credit is not a hard spending cap. Scale down or delete the demo after judging if it is no longer needed.

Build preparation downloads approximately 1.1 GB of model weights plus dependencies and a pinned public migration guide. Startup verifies the model files and loads one float32 CPU model. Source/model preparation requires network access; request-time reviews fetch no supplied URLs and call no model API. Use one worker: increasing workers duplicates the model and breaks the process-local concurrency/rate budgets.

## Verification results and boundaries

1. Public health returned `200` with `{"status":"ready"}`; Render reported the deploy as `live`.
2. The public Kong example showed REVIEW REQUIRED, the readiness-path change, five retained passages and five model windows.
3. Sanitized mobile uploads also produced a five-window review. Both JSON and Markdown downloads were checked from the example report.
4. The public request without a CSRF token returned 403. Malformed-input and unavailable-model behavior are covered by the local unit tests; an unavailable model was not deliberately forced on the public service.
5. Deployment identity, sampled memory and actual browser evidence are recorded. Best Use of Render is now listed in the article draft; publication and category acceptance remain outstanding.

The demonstration accepts at most six review attempts per minute globally, one inference request at a time and at most 32 model windows per request. Oversized/unscorable passages remain present and explicitly unscored. Input bodies are capped; temporary files are deleted after the request; logs contain counts/timing rather than input text. The server still receives uploads and trusted hosting operators can access their processing environment. This is a bounded demonstration, not a production multi-tenant service or a privacy certification.

## Event .tech domain

After the event domain is claimed, add it under the service's **Settings → Custom Domains**. Use the exact DNS records Render displays, then verify the domain and HTTPS. No generic IP address or guessed DNS record is supplied here. Add the live domain link to the article and identify Best Use of a .tech Domain only after successful verification.

## Local execution

Python 3.12 and a model-capable machine are required. In a virtual environment:

```bash
python -m pip install -r requirements-web.txt
python -m pip install torch==2.14.1+cpu --index-url https://download.pytorch.org/whl/cpu
python -m pip install transformers==4.57.1
python prepare_brief_source.py
python download_reranker.py .models/bge-reranker-base
python -m unittest discover -s tests -v
python verify_web_model.py
gunicorn wsgi:app --bind 127.0.0.1:8000 --workers 1 --threads 2 --timeout 180 --no-control-socket
```

This path does not require WSL specifically. The user can use the GitHub/Render browser setup instead of running these commands.
