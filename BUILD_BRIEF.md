# Build decision — Helm upgrade review

Decision date: October 20, 2026. Working description, not a cleared product brand.

Update: FINAL_VERIFICATION.md supersedes this initial recommendation. Current verdict is NO-GO for scaling the standalone product. The package has nine chart-render observations, artifact processing and a local model experiment that failed its extraction/citation gate. Customer demand and useful essential model contribution remain unvalidated. The positive checker label means MATCHES_SUPPLIED_FACTS, not SATISFIED.

## What we are building

A review assistant for platform engineers who repeatedly assess Helm dependency updates. It reads version-scoped migration instructions, proposes conditional requirements, and evaluates reviewed checks against supplied deployment evidence. The result is a concise review report with citations, unmet conditions and missing facts. Engineers retain deployment control.

The commercial hypothesis is that repeated investigation across upgrade PRs is expensive enough that teams will pay for maintained, tested check coverage and review history. Neither frequency nor willingness to pay has been validated. The Week 3 theme fits through automating recurring review work; that fit is our interpretation, not organizer approval.

## Rules that change our strategy

Week 3 is live. The specific rules place the entry period from October 19 at 9 a.m. PDT through October 25 at 11:59 p.m. PDT. In Lagos that is October 19 at 5 p.m. through October 26 at 7:59 a.m. Aim to submit on October 25 local time.

One entry can qualify for several genuinely used partner categories, but the participant can receive one prize in this challenge. Write-up quality has the highest judging weight. The submission needs code, a demonstration, an explanation of the open component's value, and the prescribed DEV template/tags. A new project must be built within this entry period.

The published top prize is $250, featured partner awards $200, and other partner awards $100. These are alternative award outcomes for us, not an additive prize budget. No award is assured. [1,2]

## First workflow and first useful outcome

1. An engineer supplies source/target chart identities and sanitized configuration or normalized evidence.
2. The system loads explicitly scoped, trusted public migration material.
3. An open-weight model extracts candidate conditions, required evidence, recommended action and source location. Candidates cannot become executable checks without validation and review.
4. Approved deterministic checks evaluate configuration facts. Missing external-controller information remains UNKNOWN.
5. A report tells the reviewer which specific requirement needs action or evidence. It never provides a general upgrade-safety certificate.

The first case concerns the Kong chart's documented 2.26 readiness change [3]. This is a historical regression fixture; it is not evidence of a current widespread incident. Reproduce against pinned chart archives before claiming the tool detects a real rendered upgrade issue.

## Stack decision

| Component | Choice | Reason / adoption gate |
| --- | --- | --- |
| First executable | Python 3.12 standard-library CLI | No runtime packages are required for the offline rule prototype. |
| Hosted API, later | FastAPI with validated request/response schemas | Reuse the same checker. Resolve and lock actual dependency versions when implementing this slice. |
| Interface, later | A small report page using server-rendered HTML | The main output is an evidence report; a large frontend framework has no demonstrated benefit yet. |
| First model benchmark | Qwen/Qwen3-8B | Open-weight Apache-2.0 candidate with an external-serving path [4]. Quality remains unmeasured. |
| Initial model access | Backboard, subject to authenticated catalog and price checks | Use explicit model/provider settings. The account must actually expose the chosen open model; an SDK installation proves no access. Compare candidates on the same extraction task [5]. |
| Public delivery | Render | Host the report API/interface after the local path works. No claim that a small web service can serve an 8B model itself. |
| Public address | Claimed Hacktoberfest .tech domain | Add to the functioning service after confirming redemption and DNS. |
| Storage | Local JSON reports initially | Add durable, tenant-isolated storage when hosted/private jobs actually require it. An ephemeral web-service filesystem is insufficient for retained customer reports. |
| Training experiment | Tinker, conditional | Only after a baseline failure, enough independent labels, and a clear held-out evaluation. Its category requires actual fine-tuning and demonstrated improvement [1,6]. |

No vector database is needed for a few explicitly selected migration documents. Fetch/cache known public sources first. Do not copy private deployment configuration into a public-doc retrieval index. Do not install CUDA, download weights, or provision a GPU for this hosted-access baseline.

If the Backboard catalog lacks a suitable model or usable pricing, change the access provider after checking the alternative. Do not silently substitute a closed model and claim open-weight inference. “Zik Pro” remains unidentified until an exact name or URL is supplied; it is not part of this implementation decision.

## Sponsor entries: evidence required

| Category | Planned position | What must exist before listing it |
| --- | --- | --- |
| Overall | Primary target | Working open-AI workflow, measured useful work, strong clear write-up. |
| Render | Intended | Live service running on Render, with deployment evidence. |
| Backboard | Intended, access conditional | Actual open-model extraction/comparison through Backboard and reproducible outputs. |
| .tech | Intended | Functioning demo on the domain redeemed through this event. |
| Tinker | Stretch experiment | Trained model and held-out evidence of improvement over the baseline. |
| Sentry Agent Tracing | Optional after real inference | Useful traces and a documented debugging finding. SDK installation alone is insufficient. |

Other sponsor services are not in the initial implementation plan. Temporal needs a workflow whose restart/retry requirements justify it; MongoDB Atlas and Tiger Data need an actual storage/retrieval need; Browserbase needs a genuine browser task. No duplicated hosting or databases for category count. TabPFN is aimed at tabular prediction and the challenge describes a non-commercial local license for its recommended version [1]; that requires separate commercial licensing assessment if ever considered. It does not fit this task today.

## How we avoid a thin AI wrapper

The reusable value must be source/version provenance, tested requirement coverage, correct abstention and useful review artifacts. A model summarizes the unfamiliar prose; the checker must verify explicit facts. Requirements that need runtime or human evidence stay unresolved until that evidence exists.

Renovate already updates chart dependencies [7]. helm-diff already compares rendered changes [8]. helm-migrate-values already applies chart-supplied values migrations [9]. We should work alongside these tools. The experiment is whether broader conditional migration obligations can be extracted and checked with less reviewer effort.

The first Kong rule is easy to reproduce manually. It cannot be a defensible commercial advantage by itself. The model must help across independent migration sections, while maintained coverage must cost less to produce than customers will fund. If that fails, the scalable-product thesis fails even if the demo looks good.

## Evidence gates

Current result: 14 offline tests passed on synthetic assertions. They cover missing information, supported scope, version boundaries, ambiguous tags and probe interpretation. This is a rule-contract result. No model accuracy, real Helm behavior, time saving, paid demand or production reliability has been established.

Next technical gate: reproduce the first case from immutable chart inputs, with explicit Helm/Kubernetes target settings, without live-cluster credentials. Then test at least one independently labeled migration section. Version conflicts, unsupported transitions and absent facts must not produce unsupported satisfaction claims.

Next model gate: compare manually reviewed rules, a strong prompted model/coding assistant, and the candidate extraction-plus-checker workflow on the same cases. Track omitted requirements, wrong applicability, unsupported satisfaction, source accuracy, correct abstention, human review time, tokens, latency and billed cost. Split by independent migration section/chart family. Do not train on the evaluation examples and call them held out. Public docs may have appeared in pretraining.

Next customer gate: obtain three qualified conversations and one authorized real upgrade review. These are proposed research targets, not validated traction. Find the repeat workload, current alternative and budget owner. A paid pilot supplies better evidence than compliments. No outreach has been sent.

## Working schedule and spending

- October 20: offline checker baseline, pin chart inputs and prepare labels.
- October 21: first real rendering and model baseline, including failure cases.
- October 22: keep or reject the model workflow based on results; training only if justified.
- October 23: authorized external review if a suitable evaluator is available; otherwise disclose author-only evaluation.
- October 24: hosted report and measured demonstration; draft the write-up.
- October 25: test the submitted path, freeze the entry version, publish using the official template. Record later changes as required.

These are work targets, not promises that access, a customer or results will arrive on schedule. Reserve substantial time for the write-up because it carries the greatest judging weight.

Budget only confirmed, redeemed provider balances. The photographed offers do not prove that credits have been applied, that inference is covered, or when balances expire. Confirm scope, expiry, auto-reload and service pricing before paid calls. No paid infrastructure or provider usage has been initiated. No unspecified large funding offer is included in the plan.

Post-event, test a bounded paid review/pilot before an unlimited subscription. Track model, render, storage, retries, support and rule-maintenance cost separately. Repeated bespoke investigation may support a service business rather than SaaS; be honest about that outcome.

## Sources checked October 20, 2026

1. Week 3 prompt and partner requirements: https://dev.to/challenges/hacktoberfest-week3-2026-10-19
2. Specific entry period and rules: https://dev.to/page/hacktoberfest-week3-2026-10-19-contest-rules
3. Kong guide: https://github.com/Kong/charts/blob/main/charts/kong/UPGRADE.md#2260 — file Git blob SHA `893527759a66e5293aded6999f8c6879b634c6d6`, not a commit ID.
4. Qwen model card: https://huggingface.co/Qwen/Qwen3-8B
5. Backboard model catalog and explicit routing: https://docs.backboard.io/concepts/models
6. Tinker supported models and pricing: https://tinker-docs.thinkingmachines.ai/tinker/models/models_and_pricing/
7. Renovate Helm manager: https://docs.renovatebot.com/modules/manager/helmv3/
8. helm-diff: https://github.com/databus23/helm-diff
9. Values migration plugin: https://github.com/OctopusDeployLabs/helm-migrate-values
