# Verification verdict — October 20, 2026

Current status: CONTEST_READINESS.md supersedes this document for contest requirements and sponsor decisions. HACKATHON_BUILD.md records the later bounded CLI/browser implementation, 58 passing tests and executed open-weight inference. The commercial NO-GO below remains. Its earlier extraction failure is not a reason to block the separate, narrower hackathon build. The original tables below describe the historical checker/extraction stage; the complete contest submission remains unpublished.

## Decision

Historical commercial verdict: NO-GO for scaling the standalone commercial product on the evidence available at that stage. This does not prohibit the later bounded hackathon browser demo or useful hosting. Paid training and additional platform features still require evidence of need; current contest work is tracked in CONTEST_READINESS.md.

This decision is narrower than declaring the technical problem worthless. It reflects failed extraction, unresolved buyer value and closer competitive overlap. A future bounded extension needs a demonstrated gap on an authorized real workflow, not a stronger novelty slogan.

## Gates and evidence

| Gate | Result | Evidence / remaining requirement |
| --- | --- | --- |
| Local artifact processing and abstention | PASS within tested scope | 32 tests total: original 14 plus 18 artifact/adversarial tests. Includes missing controller facts, content tampering, stale/future timestamps, namespace mismatch, duplicate resources/keys, unsupported images, aliases, path escape and parser limits. |
| Documented chart configuration observations | PASS for rendering only | Previous nine observations across official Kong and kube-state-metrics chart artifacts remain recorded. No application HTTP behavior or live upgrade was exercised. |
| Artifact-to-live-system identity | NOT VERIFIED | Checksums bind local bytes. They do not authenticate a cluster, caller, capture time, controller ownership, or chart-to-render provenance. A test intentionally shows that changing a file and its expected hash can produce a configuration match while live authentication remains false. |
| Small local model extraction candidate | FAILED this configuration | Six Qwen3-0.6B runs: all JSON-readable; only one met the frozen output/citation contract. Author review found important missing conditions or incomplete actions. |
| AI advantage over a strong model and normal review | NOT RUN | No hosted credentials are configured. No strong coding-assistant comparison or measured human review-time study exists. |
| Claimed worldwide novelty / unique packaging | NOT ESTABLISHED; close overlap found | ShiftScope already has semantic migration rules, an analyzer SDK and CI output; KubePreflight documents evidence-aware upgrade checks and incomplete-coverage behavior. Neither was benchmarked end to end here. |
| Repeated customer problem and buying decision | UNVALIDATED | No customer interview, authorized private evaluation, repeated adoption or payment. Public upstream reports are not purchasing evidence. |
| Sustainable delivery economics | UNVALIDATED | No measured support/rule-maintenance workload, sale price or margin. Local CPU inference is not proof of a free production service. |
| Hackathon completion and sponsor qualification | NOT DEMONSTRATED | Extraction is a separate failing experiment, not an essential validated part of the checker. No complete deployed/video demonstration, submission or genuine sponsor integration has been completed. |

The table deliberately does not convert every NOT RUN into a failure or every unit-test pass into product approval. There is no all-gates-passed result.

## What changed in the implementation

`review_artifacts.py` now extracts image/probe facts from selected Deployment documents rather than relying entirely on arbitrary reference strings. It checks explicit resource identity, local path scope, SHA-256, bounded file sizes, asserted snapshot age and strict parsing. Separate controllers require both a manifest and a checksummed explicit relationship assertion.

An unrelated controller manifest cannot silently resolve a missing fact. A conflicting colocated/separate-controller configuration is rejected. Invalid evidence preserves UNKNOWN. Missing facts remain UNKNOWN even when the target manifest parses successfully.

The external relationship is still a caller assertion, not discovery or authentication. A selected root is assumed to be a trusted local workspace, not a filesystem concurrently controlled by an adversary. This is a local research CLI, not a hardened multi-tenant upload service. No generated commands, cluster writes or model-generated checks are executed.

Two actual rendered-manifest replays are saved in `verification/`: the proxy-only target remains UNKNOWN without external facts, while the colocated-controller render excludes this specific separate-controller condition. That exclusion says nothing about other upgrade hazards.

## Actual local model experiment

Hosted Backboard/Tinker credentials remained absent. Instead of manufacturing hosted results, a small official open-weight model was downloaded and run in the assistant's CPU environment:

- Model: Qwen/Qwen3-0.6B; immutable revision `c1899de289a04d12100db370d81485cdf75e47ca`.
- Weight SHA-256 matched published LFS metadata. Metadata/tokenizer file identities and actual environment versions are recorded.
- Four focused public-document tasks plus two synthetic checks. Prompt, obligations, source hashes and sampling settings were frozen before generation.
- Six outputs parsed as JSON. Five failed the required short, exact source-quote contract. The abstention case passed that contract.
- Total generation time: 74.892 seconds; peak process RSS: 4750.1 MiB. Model loading, preparation and downloads are excluded from generation time.
- No provider model API calls, fine-tuning or paid deployments. Compute economics have not been established.

Author review, separate from the mechanical citation check:

| Case | Observed limitation |
| --- | --- |
| Kong readiness | Omitted the controller-version bound and separate-deployment condition; did not give the specific endpoint remedy. |
| Kong plugin writes | Preserved the conditional plugin issue and alternatives in outline, but the configuration action was incomplete and citation formatting failed. |
| kube-state-metrics | Listed health endpoints without capturing the crucial self/telemetry location. |
| ESO stored version | Mentioned the version concern but did not clearly identify the required CRD status field and absence condition. |
| Insufficient information, synthetic | Correctly abstained. |
| Appended adversarial instruction, synthetic | Did not emit deployment approval, but still omitted required readiness conditions. |

The combined quote validator checks exact substring and a six-word length limit. Failure is not automatically a hallucination: line-break normalization or excess length can cause it. The semantic omissions above are the more important product issue.

This is an author-reviewed smoke test, not independent accuracy measurement. Documents overlap across cases, public text may be in pretraining, and the model is much smaller than the original Qwen3-8B candidate. It does not establish that larger models or a revised extraction method cannot work. Conversely, it supplies no reason to select this tested configuration or train it just for a sponsor entry.

Exact original outputs are retained locally and hashed; published result records omit source quotations. The bundle includes the frozen contract, metrics, original-output hashes and a rerun harness. Weights, source snapshots, environment caches and full raw outputs are excluded from the deliverable.

## Competitive verification

Follow-up execution is now recorded in `verification/TOOL_COMPARISON.md` and `tool-comparison-results.json`: Helm strict lint passes both Kong chart versions and the pinned ShiftScope Helm 4 analyzer emits the same four readiness findings. The latter has a different migration scope; this is not evidence that it failed its purpose. The earlier plain diff exposes the relevant endpoint change. This bounded comparison leaves the NO-GO decision unchanged and does not replace buyer or live-workflow validation.

ShiftScope was cloned read-only at commit `b67c4a8694749418f42385b2aa1b36ef1e4c48a0`. Its README, core models/rule interface, Helm 4 rules and optional augmentation helper were inspected. The SDK and structured findings are implemented source, not only a product-page claim. Its inspected Helm analyzer concerns Helm 4 readiness; this inspection does not establish complete coverage of our Kong requirement or operational performance.

The examined augmentation helper wraps deterministic findings and supports a supplied summarizer callback. Its built-in helper shown in that snapshot produces a templated summary; we did not infer that it performs our prose-to-requirement extraction. This qualification prevents overstating the competitor's AI implementation.

KubePreflight's public documentation describes a local CLI/console, evidence-backed findings, explicit incomplete evidence and applicability/coverage semantics. Its claimed EKS validation was not independently reproduced here. Camunda documents a local toolkit that migrates overrides and checks configuration while explicitly distinguishing a clean report from deployment readiness.

These projects weaken novelty claims for semantic migration analysis, a CLI/CI wrapper, structured findings and conservative evidence reporting. They do not prove that every particular application-migration requirement is solved. Any next implementation should first evaluate extending or integrating with existing work.

Primary sources:

- https://github.com/thc1006/shiftscope
- https://github.com/thc1006/shiftscope/blob/b67c4a8694749418f42385b2aa1b36ef1e4c48a0/src/shiftscope/core/models.py
- https://github.com/thc1006/shiftscope/blob/b67c4a8694749418f42385b2aa1b36ef1e4c48a0/src/shiftscope/ai/augment.py
- https://github.com/imneeteeshyadav98/kubepreflight
- https://docs.camunda.io/docs/8.8/self-managed/deployment/helm/operational-tasks/camunda-helm-toolkit/
- https://huggingface.co/Qwen/Qwen3-0.6B
- https://dev.to/challenges/hacktoberfest-week3-2026-10-19

## What is required to change this verdict

An authorized real review must show a requirement that existing tools or the team's normal workflow leave unresolved, and our method must reduce total effort without introducing unsupported confidence. A person capable of buying the service must show repeated need. Model extraction must preserve critical conditions and pass independent evaluation before influencing operational checks.

A disposable authorized runtime is required for application-level validation. An actual hosted-model account is needed for the originally proposed provider comparison. Customer interviews require actual people and responses. Those gates cannot be completed by generating more synthetic fixtures or claiming a global search proved uniqueness.

No outreach was sent, no third-party project was changed, and no cloud infrastructure was created. The engineering artifacts are useful for continuing a carefully scoped investigation or proposing an improvement to an existing project. A scalable paid platform and international recognition remain outcomes to earn, not verified properties of this prototype.
