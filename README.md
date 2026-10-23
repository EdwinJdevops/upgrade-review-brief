# Upgrade Review Brief

Prepare a source-linked Helm migration review from two rendered Deployment manifests, in a browser or from the command line.

The tool identifies changes in selected container fields, uses the open-weight BAAI BGE reranker to order migration passages, and preserves unresolved questions and source locations for a human reviewer.

The included Kong example shows a readiness-path change and missing context about a separately deployed controller. Every selected-section passage remains available. A successful report is never permission to deploy.

## Run from a browser

The Flask interface supports the controlled Kong example and sanitized file uploads. It runs the same open-weight model, shows the focused diff, keeps every passage locator and exports JSON/Markdown. Request-time source URLs are recorded, never fetched. Files uploaded to a hosted instance are processed on that server; they are not kept as a history. See [Render setup and operating limits](RENDER_DEPLOYMENT.md).

**Live demo:** [https://upgrade-review-brief.onrender.com](https://upgrade-review-brief.onrender.com). Render runs the Python application and the verified BGE CPU model in one `1c-2g` instance. Actual public-browser checks passed for the example, sanitized uploads, secure session cookie and both downloads. See [deployment evidence](verification/render-deployment-2026-10-23.json). [Contest readiness](CONTEST_READINESS.md) records the remaining submission requirements and sponsor decisions.

Open [Actions](https://github.com/EdwinJdevops/upgrade-review-brief/actions) and select **Test and demonstrate upgrade review**. Choose **Run workflow**, enable `run_model`, and run it on `main`. The workflow tests the code, downloads verified model files, runs CPU inference and writes the actual review brief to its run summary. No WSL, GPU or model API key is needed on your device.

A push to main with `[model-demo]` in its commit message also requests the model job. Normal pushes run fast tests only. This keeps model downloads explicit. Standard public-repository GitHub-hosted runners are used; account policies and external download availability can still block a run.

## Version-range review

The browser now supports Kong 2.18.0 → 2.26.0 as a controlled multi-change example. Leaving the section field blank selects stable release headings between the supplied chart versions and retains unversioned guidance. Each changed field receives its own source-reading suggestions and an explicit coverage ledger. At most six change queries and 32 model windows are evaluated; unscored material and changes beyond that query limit stay visible.

A frozen author-labeled comparison found both prerequisite passages within the model’s top two readings per change, versus one of two for keyword matching. The combined model query also covered both within four readings. This is one controlled chart example, not independent accuracy, user-time or commercial validation. See [new evaluation](verification/range-evaluation-results.json) and [implementation/validation notes](PRODUCT_EVOLUTION.md).

For local or CI use, no case JSON or manually calculated hashes are needed:

```bash
python review_change.py --before before.yaml --after after.yaml --guide UPGRADE.md \
  --deployment my-deployment --namespace my-namespace \
  --source-url https://example.org/guide --model-dir .models/bge-reranker-base
```

Use `--fail-on-unreviewed-changes` in CI to emit the report and exit **3** when manifest edits fall outside the focused review. Exit 0 still means **REVIEW_REQUIRED**, never upgrade approval. Exit 2 means invalid input or review failure.

Use `--format json` for machine-readable output, `--section` for an explicit heading, or `--lexical-baseline` for the labeled non-model comparison. No chart execution, source URL fetching or cluster writes occur in this review command.

## Manifest coverage inventory

The report now inventories every named resource in both supplied renders and marks additions, removals and content changes outside the focused review. For the controlled Kong range, this reveals **three resources with edits outside scope**: the Deployment, Service and ServiceAccount. Some edits are metadata; the inventory assigns no severity and does not infer that a resource is broken.

For the selected Deployment, fixed categories identify other edited settings, such as replicas, environment/probe configuration, volumes or init containers. Their values and arbitrary field names are withheld from exports and model queries. Resource identifiers remain visible. Duplicate identities, unexpanded Kubernetes Lists and non-JSON YAML are rejected before inference. Namespace/API-version interpretation is literal; this is not Kubernetes semantic validation. Unchanged resources can still carry migration obligations.

The update passes **85 unit tests**, including the real CLI exit behavior and browser redaction boundaries. [GitHub Actions](https://github.com/EdwinJdevops/upgrade-review-brief/actions/runs/39975786774) passed. These tests use scorer doubles, not accuracy measurements. The same application revision is live on Render; [separate actual-model HTTP checks](verification/render-manifest-coverage-2026-10-23.json) verify the range inventory and sanitized Secret/replica-change upload with system TLS validation. [Public desktop/mobile checks](verification/render-coverage-browser-2026-10-23.json) also passed with real inference and both downloads; the browser proxy certificate exception is recorded. Dated results for preceding releases below remain historical.

## Current assessment

A working migration-review feature; commercial adoption and general incremental AI value remain unvalidated. [Current audit and next steps](AUDIT_AND_NEXT_STEPS.md) records seven concrete weaknesses and a new same-input ablation: keyword matching and BGE chose the same first demo passage. The model changed the lower reading order, not the manifest findings. Original application code has no selected LICENSE yet; upstream model and dependency terms are separate.

## Current evidence

- The version-range feature is live and the final revision passed 68 tests in GitHub Actions. Full public desktop/mobile checks and the targeted follow-up are tied to their exact revisions in the [release record](verification/render-range-release-2026-10-23.json). The controlled range review retains 16 source passages and evaluates 32 model windows.

- The Render deployment is live. Public desktop/mobile checks exercised real inference: five evaluated windows and five retained passages per example/upload. [Public browser evidence](verification/render-public-browser-2026-10-23.json) records the checks and the execution proxy certificate exception.

- The browser version now passes 68 tests. Actual-model desktop and mobile browser checks cover the example, file uploads and JSON/Markdown downloads; see [browser evidence](verification/web-browser-2026-10-23.json). This is local execution, not a Render deployment.
- [Watch the genuine browser demonstration](docs/demo/browser-demo.mp4). It shows real inference through the local browser interface. [Home screen](docs/demo/home-desktop.png) · [Review screen](docs/demo/report-desktop.png).

- [GitHub Actions run #1](https://github.com/EdwinJdevops/upgrade-review-brief/actions/runs/39942834494) passed on October 23, 2026: all 45 tests and the CPU model demonstration succeeded. The model made five evaluations and omitted no passages.
- The local model demo and clean-package replay from October 20 are preserved in `verification/`.
- A six-query author-defined ranking check placed the expected passage uniquely first six times; a simple keyword baseline did so five times, tying on the remaining query. This is a small feasibility check, not a representative accuracy or customer-benefit result.
- No measured reduction in total reviewer time, live-cluster readiness test, production use or commercial demand is claimed.

Read the [recorded brief](verification/demo-brief.md), [machine-readable result](verification/demo-brief.json) and [build scope](HACKATHON_BUILD.md).

## Run locally

Requires Python 3.12. The full test suite needs the small web dependencies; the lexical comparison needs only PyYAML:

```bash
python3 -m pip install -r requirements-web.txt
python3 -m unittest discover -s tests -v
python3 prepare_brief_source.py
python3 upgrade_brief.py brief-cases/kong-readiness.json --root . --lexical-baseline
```

For the executed model configuration, use an isolated environment:

```bash
python3 -m pip install torch==2.14.1+cpu --index-url https://download.pytorch.org/whl/cpu
python3 -m pip install transformers==4.57.1 PyYAML==6.0.3
python3 download_reranker.py .models/bge-reranker-base
python3 upgrade_brief.py brief-cases/kong-readiness.json --root . --model-dir .models/bge-reranker-base
```

The pinned weight file is approximately 1.1 GB. Add `--format json` for machine-readable output. Runtime memory and speed vary by host. The inference path is local after preparation; no hosted model service is called.

## Coverage

One explicitly selected Deployment is compared: images, HTTP probe path/port and container read-only-root settings. Other resources and fields can contain important changes. Users can explicitly select one documentation section or automatically select stable release headings in the supplied version range. The coverage ledger does not authenticate the guide or prove complete version history.

Input hashes establish correspondence to supplied bytes, not source authorship, a live cluster, controller ownership or chart-render provenance. Model scores describe relative relevance, not confidence or applicability. Over-limit material remains explicitly unscored. The local workspace and runtime are assumed to be operator-controlled.

## Submission status

Work began October 20, 2026 for the Week 3 challenge. Code and CI publication do not by themselves constitute a DEV submission. The [article draft](DEV_SUBMISSION_DRAFT.md) includes the verified repository and successful demonstration links. It has not been published to DEV. The article targets the published GitHub Actions option within Best Use of GitHub Copilot; category acceptance and awards remain unverified. GitHub Copilot itself was not used.

[Attribution](THIRD_PARTY_NOTICES.md) records upstream sources. The earlier failed model trials and bounded existing-tool comparisons remain available rather than being represented as successes.
