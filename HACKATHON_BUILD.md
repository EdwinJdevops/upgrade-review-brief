# Upgrade review brief — bounded Hacktoberfest build

Browser implementation update, October 23: the project now includes a Flask browser interface, bounded sanitized uploads, JSON/Markdown downloads, Render configuration and 58 passing tests. An actual-model browser-route check passed locally (five evaluated windows, all five passages retained). Render deployment and DEV publication remain unfinished. See CONTEST_READINESS.md for current requirement/category status; the sections below retain earlier implementation-stage history.

Earlier publication evidence: [GitHub Actions run #1](https://github.com/EdwinJdevops/upgrade-review-brief/actions/runs/39942834494) passed the then-current 45 tests and CPU CLI demo. See verification/github-run-2026-10-23.json.

## Decision

GO for this bounded hackathon implementation. The commercial platform remains unvalidated. Customer purchasing evidence is required before a commercial expansion; it is not a prerequisite for building a working challenge prototype. The previous response incorrectly allowed the commercial gate to block hackathon engineering.

The direction changes from model-generated migration rules and a hosted approval platform to a local migration-review brief. It compares two supplied rendered Deployments, ranks an explicitly selected migration section with an open-weight relevance model, and preserves source identity, line locations and unanswered questions. It does not generate operational instructions or decide whether an upgrade should proceed.

## Implemented and executed

- `upgrade_brief.py`: checksum-verified local inputs, explicit Deployment and chart labels, limited-field diff, source section parsing, exact passage locators, local model ordering, Markdown/JSON output and lexical comparison mode.
- `rank_model.py`: BAAI/bge-reranker-base, revision `2cfc18c9415c912f9d8155881c133215df768a70`. Every required model/tokenizer/config file is verified against pinned publisher identities. Safetensors and built-in Transformers classes only; no remote Python code or provider API calls.
- Full-passage scoring uses overlapping 512-token query/passage windows with stride 32 and the maximum window logit. Windows are processed serially. Overlong queries or excessive windows remain explicitly unscored. No source passage is hidden.
- Configuration examples stay with their preceding explanatory paragraph. Scores express relative relevance, not confidence or applicability. The first relevant passage is not a complete migration procedure.
- The packaged Kong chart replay actually produced a model-ranked brief. It shows the `/status` to `/status/ready` change and calls out the unresolved external-controller context. JSON records model identities, scores, inference timings and all passage locations.
- 45 tests pass: 32 existing checker tests plus 13 brief tests. Source integrity, namespace/version selection, malformed YAML, sensitive-field exclusion, missing model scores, retained passages and condition/example grouping are covered. These do not measure user benefit.

## Actual model results and rejected attempts

The initial 0.6B generative extraction failed earlier. A new constrained A/B/C relevance-label experiment also matched only three of six author labels and mishandled the synthetic instruction-only passage. That configuration is rejected and retained as negative evidence.

The replacement BGE reranker is a purpose-trained relevance model, not a chat model asked to invent a requirement. Its first test explicitly left an ESO passage unscored because the pair exceeded 512 tokens. This was a coverage limitation; the report did not silently truncate it. Full-passage windowing was then implemented and the method/result recorded separately.

In the windowed six-query test, the expected public passage ranks uniquely first on six queries. The simple shared-token baseline ranks it uniquely first on five, with a tie on the remaining query. There are four real source sections and two synthetic distractors; several queries reuse a source section. Labels and source hashes were frozen before inference. These are author-defined feasibility cases, not independent or held-out accuracy evidence. This tiny result does not establish a general advantage over keyword retrieval, BM25, a skilled reviewer or a strong coding assistant.

Recorded CPU process peak RSS for that test: 1135.6 MiB. Summed inference time across candidate pairs: 12.3949 seconds, excluding preparation, loading and download. Weights are 1,112,206,140 bytes. These are measurements in the assistant's environment, not a speed or memory guarantee for the user's Windows/WSL laptop. No paid service was used.

Model scores can rank irrelevant or malicious source text highly. The synthetic distractor ranking test is not proof of prompt-injection security. The application limits consequences by exposing source material as review data and having no execution or approval action. Input files and the local runtime are assumed to be controlled by the operator; this is not a hardened multi-tenant upload service.

## What is deliberately absent

No new database, vector service, agent framework, cloud orchestration or fine-tuning. A small supplied document can be scored locally without those services. No current customer workflow, measured review-time reduction, live cluster behavior, production deployment or payment is claimed. Checksums authenticate bytes against caller-supplied expectations; they do not prove source authorship, live-system identity or chart-to-render provenance.

Only image, HTTP probe path/port and container read-only-root settings from one selected Deployment are compared. Environment values, Secrets, ConfigMaps, HTTP headers, annotations and commands are excluded from the model query. Other fields, resources, namespaces and chart dependencies can contain important changes. The user selects the migration section; automatic completeness across a version range is not implemented.

## Submission and sponsor position

The official Week 3 theme is Slow and Steady: automate work with an open-weight model or essential open-source AI component and explain the benefit. The model now has an actual runtime role in ordering the review evidence. That supports building this as an entry; final acceptance remains the organizers' decision. A clear English write-up and reproducible demonstration still need to be completed and published using the required DEV template.

Partner technology is optional for the overall category. One project can qualify for multiple categories through genuine usage, but can win only once in the challenge. No sponsor category is claimed from an unused credit or a logo. Render can host a useful report/demo page later; its integration has not been implemented. A claimed .tech domain could host that page if actually redeemed and configured. Tinker is not justified without a real fine-tuning comparison. Backboard is not used by the current local reranker. No partner spending or credit redemption occurred.

Target submission before Sunday evening in Lagos; official cutoff is October 25, 2026 at 11:59 PM PDT, which is October 26 at 7:59 AM Lagos. A new repository and the finished submission must remain within the published entry-window rules. The local project was started October 20. No external repository was created or published in this turn, and no entry was submitted.

## Remaining engineering work

1. Put this bounded project in its own new repository, retaining attribution and negative experiment results. Run the tests in actual repository CI.
2. Record a short demonstration: limited diff, linked migration passages, unresolved controller facts and explicit unscored/invalid-input behavior. Demonstrate both AI ranking and the lexical comparison without claiming a representative benchmark.
3. Write the DEV submission from observed outcomes, explain why local open weights help, list only genuinely used partner categories, and publish before the deadline. Do not describe the model's relevance scores as safety confidence.

Post-event commercial validation continues separately: actual reviewers, complete effort accounting, recurring need, comparative results and willingness to pay. It must not be replaced with prize results or unit-test counts.

## Primary references

- Challenge: https://dev.to/challenges/hacktoberfest-week3-2026-10-19
- Model and inference example: https://huggingface.co/BAAI/bge-reranker-base ; model card identifies MIT licensing.
- Kong guide: https://github.com/Kong/charts/blob/main/charts/kong/UPGRADE.md#2260 ; demo source is separately pinned by Git blob and SHA-256.
