# Upgrade Review Brief

Prepare a source-linked Helm migration review from two rendered Deployment manifests.

The tool identifies changes in selected container fields, uses the open-weight BAAI BGE reranker to order migration passages, and preserves unresolved questions and source locations for a human reviewer.

The included Kong example shows a readiness-path change and missing context about a separately deployed controller. Every selected-section passage remains available. A successful report is never permission to deploy.

## Run from a browser

Open [Actions](https://github.com/EdwinJdevops/upgrade-review-brief/actions) and select **Test and demonstrate upgrade review**. Choose **Run workflow**, enable `run_model`, and run it on `main`. The workflow tests the code, downloads verified model files, runs CPU inference and writes the actual review brief to its run summary. No WSL, GPU or model API key is needed on your device.

A push to main with `[model-demo]` in its commit message also requests the model job. Normal pushes run fast tests only. This keeps model downloads explicit. Standard public-repository GitHub-hosted runners are used; account policies and external download availability can still block a run.

## Current evidence

- [GitHub Actions run #1](https://github.com/EdwinJdevops/upgrade-review-brief/actions/runs/39942834494) passed on October 23, 2026: all 45 tests and the CPU model demonstration succeeded. The model made five evaluations and omitted no passages.
- The local model demo and clean-package replay from October 20 are preserved in `verification/`.
- A six-query author-defined ranking check placed the expected passage uniquely first six times; a simple keyword baseline did so five times, tying on the remaining query. This is a small feasibility check, not a representative accuracy or customer-benefit result.
- No measured reduction in total reviewer time, live-cluster readiness test, production use or commercial demand is claimed.

Read the [recorded brief](verification/demo-brief.md), [machine-readable result](verification/demo-brief.json) and [build scope](HACKATHON_BUILD.md).

## Run locally

Requires Python 3.12. The tests and lexical comparison need only PyYAML:

```bash
python3 -m pip install PyYAML==6.0.3
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

One explicitly selected Deployment is compared: images, HTTP probe path/port and container read-only-root settings. Other resources and fields can contain important changes. The user explicitly selects the documentation section; version-range completeness is not automated.

Input hashes establish correspondence to supplied bytes, not source authorship, a live cluster, controller ownership or chart-render provenance. Model scores describe relative relevance, not confidence or applicability. Over-limit material remains explicitly unscored. The local workspace and runtime are assumed to be operator-controlled.

## Submission status

Work began October 20, 2026 for the Week 3 challenge. Code and CI publication do not by themselves constitute a DEV submission. The [article draft](DEV_SUBMISSION_DRAFT.md) includes the verified repository and successful demonstration links. It has not been published to DEV. The article targets the published GitHub Actions option within Best Use of GitHub Copilot; category acceptance and awards remain unverified. GitHub Copilot itself was not used.

[Attribution](THIRD_PARTY_NOTICES.md) records upstream sources. The earlier failed model trials and bounded existing-tool comparisons remain available rather than being represented as successes.
