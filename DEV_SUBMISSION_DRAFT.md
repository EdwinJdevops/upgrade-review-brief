---
title: "A readiness path changed. Prepare the migration reading before the rollout."
published: false
tags: devchallenge, hf26challenge
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19).*

## What I Built

Kong 2.25.0 to 2.26.0 changes the proxy readiness path from `/status` to `/status/ready` in the packaged example. A manifest diff shows the path. The migration guide adds the controller question that the supplied manifests cannot answer.

Upgrade Review Brief prepares that reading for a platform engineer: a focused Deployment diff, migration passages ordered by an open-weight relevance model, input hashes, recorded source lines and a list of what still needs review. The automation assembles the review material; the engineer makes the upgrade decision. That is my interpretation of Slow and Steady: prepare the repetitive work before the human review.

## Demo

[Open the live Render application](https://upgrade-review-brief.onrender.com/). Choose **Run the model review** for the readiness example, or **Review the version range** for the broader Kong example. The range retains 16 passages and evaluates 32 model windows. Reports have JSON and Markdown export controls.

[The recorded demonstration](https://github.com/EdwinJdevops/upgrade-review-brief/blob/main/docs/demo/browser-demo.mp4) shows the earlier local single-section workflow with actual model inference. It predates the range and source-link improvements; the live demo shows the current hosted application.

## Code

[Source, Apache-2.0 licence and verification records](https://github.com/EdwinJdevops/upgrade-review-brief). The application licence is separate from the model and dependency licences. **AI coding assistance was used in development.**

## How I Built It

```text
Rendered before/after manifests + migration guide
  -> validate bytes and select one Deployment
  -> compare the supported fields; inventory other resource changes
  -> select guide sections and form change-specific reading questions
  -> BGE relevance ranking on CPU
  -> source-linked report + hashes + unresolved questions
```

The supported fields are container images, HTTP probe paths and ports, and `readOnlyRootFilesystem`. The inventory exposes other changed resources without claiming to understand their consequences. The model is `BAAI/bge-reranker-base`, pinned to revision `2cfc18c9415c912f9d8155881c133215df768a70`. It scores relevance between a question and source text. It does not write migration commands.

### Why a chat window alone is insufficient

A chat conversation can help interpret a diff. The artifact needed here is more specific: a fixed field comparison bound to supplied bytes, source line links, a section-selection ledger and retained unscored material. Generated migration advice would need to be checked against the guide. This application instead ranks the guide and records the unresolved questions. A chat-based system could implement similar controls; the interface alone does not provide them.

### What the validation does and does not show

The fresh local suite and a clean clone each ran 103 tests successfully at application revision `3cc347f04f127ccc295645ffb7a3481573f0abe2`. Tests with scorer doubles check contracts and boundaries, not model accuracy. A separate live check exercised actual inference for the original example, range review and a sanitised upload, including source-link and secret-sentinel assertions.

The specified pre-registered multi-chart backtest is unfinished. No full-set comparison with BM25 or token overlap was run, so ranking superiority is unknown. Earlier controlled Kong experiments are preserved in the repository, but they are not a substitute for that benchmark.

| Required backtest | BGE | BM25 | Token overlap |
| --- | --- | --- | --- |
| Pre-registered multi-chart cases | NOT RUN | NOT RUN | NOT RUN |
| Top-1 / top-3 / top-4 / MRR | Unavailable | Unavailable | Unavailable |

A separate reproducibility check found a real limit. Ten same-machine CLI runs produced matching normalized hashes. The GitHub runner comparison failed because score floats differed. Passage order matched in that comparison, but I dropped the general determinism claim. Neither pinned weights nor a fixed seed guarantees identical floating-point output across environments. The failure and both outputs remain in the repository.

The supported thesis is a source-pinned, hash-bound review artifact whose workflow can be rerun. The broader ranking experiment has not established that the model beats keyword search, and cross-environment byte-identical output is not claimed.

### Render decisions

Render runs the Python application and actual CPU inference in the same service. The configured plan is `1c-2g`, listed at $25 per month for compute before other charges. It runs one worker with two threads and allows one inference at a time. The model loads at boot, and `/healthz` reports readiness and the deployed git revision. Automatic deployment is off.

The following are end-to-end HTTP measurements from this test client, including the form GET and review POST. Percentiles use successful serial requests only; every failed attempt remains in the raw log. They include client/network overhead and are not model-only timings.

| Request | Attempts | Failures | p50 | p95 |
| --- | --- | --- | --- | --- |
| Readiness example | 20 | 0 | 10.300 s | 11.856 s |
| Range review | 10 | 0 | 19.403 s | 21.538 s |

The raw concurrency results retain every response, including rejections. This is a bounded service check, not a production load test. In the two-request burst, 1 request returned HTTP 200 and 1 returned HTTP 429. In the five-request burst, 1 returned HTTP 200 and 4 returned HTTP 429. Rejected users saw: “Another review is running. Try again when it finishes.” The highest logged sampled Python-process RSS was 1075441664 bytes, sampled every 10 ms during inference. This does not measure total service memory or an exact instantaneous peak.

The deployment uses Render’s native Python build, not a Docker image. Docker was unavailable in the development environment; no container build is claimed. A cold-start experiment and a fresh-service Blueprint test remain unrun, so the README does not include a tested Deploy button.

## Why Does Open Innovation Matter?

The pinned weights and tokenizer make the ranking component available for local inspection and inference without a hosted model API key. The loader verifies the recorded file identities and uses local files with remote model code disabled. The packaged Kong guide links to a recorded upstream commit. These controls make inputs and sources inspectable; they do not prove that a passage applies to a cluster.

The local CLI lets the operator keep review inputs on their own machine after preparation. The public Render demo processes uploads on its server. Those are different privacy choices, so only sanitised material belongs in the public demo.

### Scope and limits

This is a focused review-preparation tool, not an upgrade approval gate. It cannot infer live cluster state, assess every Helm change, authenticate an uploaded document against its URL or certify an upgrade path. All reports remain **REVIEW REQUIRED**. Independent reviewer benefit, ranking accuracy across charts and production capacity are unvalidated.

### What is next

Next I will complete the pre-registered multi-chart benchmark and obtain independent labels before deciding whether model ranking earns its runtime cost. Then I will observe engineers reviewing their own upgrades, including missed prerequisites and the work required to prepare the inputs.

### Attribution

[Kong charts and migration guidance](https://github.com/Kong/charts/blob/b39300d09d6d70297dc437015d4a49e484b7b77d/charts/kong/UPGRADE.md), [BAAI’s BGE model](https://huggingface.co/BAAI/bge-reranker-base), PyTorch, Transformers, Helm, PyYAML, Flask, Jinja and Gunicorn supply upstream work. [Third-party notices](https://github.com/EdwinJdevops/upgrade-review-brief/blob/main/THIRD_PARTY_NOTICES.md) record attribution.

## Prize Categories

**Best Use of Render.** Render is the deployed AI runtime: it loads and runs the open-weight model, accepts bounded uploads, serves the review report and reports readiness. The entry targets this category only.
