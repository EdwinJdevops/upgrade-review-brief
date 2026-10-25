# Remaining checks and exact commands

Run from the repository root. Preserve new outputs in a new directory.

## Existing executable checks

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-web.txt
.venv/bin/python -m unittest discover -s tests -v
```

Actual hosted checks, replacing LIVE_SHA with the revision returned by /healthz:

```bash
.venv/bin/python verification/verify_manifest_coverage.py --commit LIVE_SHA --output verification/closeout/live-functional-repeat.json
python verification/measure_render.py --expected-sha LIVE_SHA --output-directory verification/phase3/live-repeat
```

For a local model rerun, the native build script installs the CPU dependencies and prepares verified inputs. It is the deployed Render build command, not a Docker build:

```bash
bash render-build.sh
.venv/bin/python verification/check_determinism.py --runs 10 --model-dir .models/bge-reranker-base --output-directory verification/phase2/local-repeat
```

Use the same active Python environment for bash render-build.sh and later commands. The model is large; the successful native deployment is recorded separately.

## NOT RUN or not implemented

- Pre-registered multi-chart backtest: no runnable command exists. The script, case selection and labels were not implemented. Follow the owner's Phase 4 protocol, commit labels before scoring, and disclose this new run. No invented command is supplied.
- Reusable GitHub Action: no action.yml exists, so no runner command or pass can be reported. Remove entry claims rather than confuse the existing workflow with a delivered reusable Action.
- Docker image: no Dockerfile or container build exists. The conditional Docker deliverable was omitted; native Render deployment is the tested alternative. There is no honest Docker command for this repository yet.
- Cold restart: requires an authorized Render restart outside the available connector; record revision and timestamp, then measure the first successful response on the restarted instance. Rolling-deploy duration is not a substitute.
- Disposable Blueprint install: requires a create/test/delete path. Do not create a paid test service without an available cleanup operation. The Deploy button is removed.
- Fresh mobile browser and saved screenshots: local Chromium installation failed; the cloud browser exposed desktop interaction but no viewport-resize or artifact-saving operation was used. Repeat at desktop and mobile widths using a browser with these capabilities, including both downloads and sanitised upload.
- DEV publication: deliberately not performed. Review DEV_SUBMISSION_DRAFT.md, confirm personal entrant representations, then publish using the official template and tags before the verified deadline. Publishing the repository alone is not submission.
