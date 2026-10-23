# Upgrade-review investigation and executed evidence

Research and execution date: October 20, 2026. Prepared for Edwin Jonathan.

Historical phase record: FINAL_VERIFICATION.md supersedes the model/test status and product recommendation below. Subsequent work added artifact checks, six actual local model runs and closer competitor inspection; it did not establish product approval.

## Decision

Continue a bounded experiment on application migration requirements inside existing upgrade-review workflows. Do not expand into a general Kubernetes control plane. The technical problem is credible; buyer demand, differentiation, model contribution and commercial economics remain unvalidated.

The public record now supports more than our original single Kong example, and two chart families were rendered using pinned official artifacts. It also exposes stronger competitors and causal ambiguity. Those findings narrow the opportunity rather than establish a business.

## What was actually done

- Searched public upstream issues, project migration documentation, vendor product documentation and public pricing.
- Selected six upstream records for an evidence ledger: five user reports and one project migration guide. Read discussion on four reports, including contrary explanations and later counterexamples.
- Downloaded official Kong chart packages 2.25.0 and 2.26.0 and kube-state-metrics 5.26.0. Verified their SHA-256 values against publisher index entries.
- Downloaded official Helm 3.12.3 for a historical rendering experiment and checked its published SHA-256. No independent signature verification was performed.
- Executed nine controlled rendering cases, preserving inputs, commands, manifest outputs and hashes. All nine observation assertions matched expectations.
- Compared selected rendered fields with a plain diff baseline. The relevant probe/image changes are visible without AI.
- Replaced the prototype's positive SATISFIED label with MATCHES_SUPPLIED_FACTS and its negative counterpart with CONTRADICTS_SUPPLIED_FACTS. All 14 existing rule-contract tests still pass. Assertions remain unauthenticated.

No customer was interviewed or contacted. No paying customer, time saving, production incident avoidance, model accuracy, fine-tuning result or live Kubernetes behavior was established. Model credentials are not present in this runtime; account balances and account-level model access remain unknown. Zero model requests or paid deployments were initiated.

## Public evidence and its limits

This is a purposive sample found through targeted searches. It has no denominator of all upgrades and cannot estimate incident frequency, market size or a willingness-to-pay rate. Several records concern the same ESO migration, so they must not be counted as independent demand signals.

| Record | Observed public evidence | Qualification |
| --- | --- | --- |
| ESO #4662, opened April 2025 [1] | Project migration instructions require examining stored API versions and CRD ownership/installation mode. | A requirement source, not a customer incident. It demonstrates that rendered target YAML alone cannot supply every prerequisite. |
| ESO #5478, opened October 2025 [2] | User describes GitOps drift and a large manifest migration. Discussion attributes some behavior to client-side fetching and later reports distribution differences. | User-reported scale, not independently verified. Closed thread, mixed causes and suggestions; do not encode the title as a proven root cause. |
| ESO #4816, opened May 2025 [3] | User associates an upgrade jump with missing SecretStores; a project member disputes a reproducible product defect and questions the path. | A negative control for our interpretation process. The title does not establish a universal data-loss bug. |
| kube-state-metrics #4981, opened November 2024 [4] | User reports readiness breakage after an image override. Discussion links a fix and later questions a self-monitoring configuration. | Historical failure report with important configuration qualifications. Our experiment verifies manifest properties only. |
| postgres-exporter #3792, opened September 2023 [5] | User reports removed custom-query behavior being mistaken for a renamed configuration. Another commenter reports similar difficulty. | Closed for inactivity in 2025. This is historical evidence about migration interpretation, not a verified current defect. |
| kube-prometheus-stack #7230, opened September 2026 [6] | User reports stricter collectors rejecting file-based ServiceMonitor credentials after a dependency change. | Recent but not reproduced here. Closed status and a request for a PR do not establish a verified resolution. |

The common hypothesis is narrower than "Helm is broken": compatibility can depend on application versions, external controllers, active API state and deployment settings that a chart version or valid manifest does not fully express. The evidence does not establish that a new third-party product is the best solution.

## Executed chart experiment

Configurations are author-controlled lab fixtures, not customer data. Kong cases use Kubernetes target 1.27.3; kube-state-metrics cases use 1.29.10. Helm receives no live cluster configuration. Historical versions are regression fixtures, not deployment recommendations.

| Controlled change | Actual rendering observation | Supported conclusion |
| --- | --- | --- |
| Kong 2.25.0 to 2.26.0, proxy 3.3.0, controller disabled in chart | Readiness path changes from `/status` to `/status/ready`. | Reproduces the documented manifest change. |
| Explicit Kong readiness override | Target path becomes `/status`. | The described configuration remedy is expressible in the target chart. |
| Colocated controller 2.10.4 | Target falls back to `/status`. | The chart handles a known colocated combination. |
| Proxy 3.2.0 | Target falls back to `/status`. | Proxy version changes rule applicability. |
| Disabled controller image setting changed to 2.11.0 | Proxy-only target still uses `/status/ready`. | An unused controller image setting establishes no external-controller version. |
| kube-state-metrics image v2.13.0 to v2.14.0 in chart 5.26.0 | Image changes; `/readyz` stays on port 8080. | Application changes can invalidate assumptions without a corresponding probe change. |
| Enable self-monitoring with the same image override | Telemetry port appears; readiness still uses 8080. | Effective settings must be examined before recommending a universal remedy. |

The last three assertions concern one chart family, the first six another. Nine passing observation assertions are not nine detected production failures. Kong's actual external controller was not deployed or observed. The kube-state-metrics v2.14.0 README places `/readyz` on its telemetry endpoint [7]; no HTTP server or readiness outcome was tested here.

The plain diff baseline exposes the changed probe in Kong and the changed image in kube-state-metrics. Therefore, we cannot claim that diff tooling misses these changes. The proposed additional work is interpreting applicability, asking for missing facts and linking a check to a supported migration requirement. Whether that saves total review effort remains open.

## Competition changes the product boundary

| Existing option | Publicly documented overlap | Consequence |
| --- | --- | --- |
| Plural Upgrade Autopilot [8,9] | Preflight analysis, compatibility information, version selection and upgrade automation; documentation describes scraping compatibility sources and generating PR/pipeline actions. | A broad AI upgrade platform would face close competition. We have not tested its exact coverage of our cases. |
| Kubegrade [10] | Advertises upgrade readiness analysis, dependency risks, configuration blockers and operational workflows. | Do not pitch upgrade readiness or a Kubernetes control plane as an unoccupied market. Claims have not been benchmarked here. |
| Renovate [11] | Updates Helm dependencies. | Consume existing upgrade proposals instead of duplicating dependency update automation. |
| helm-diff [12] | Shows rendered upgrade differences. | Add interpretation only if it improves the review outcome beyond the visible diff. |
| helm-migrate-values [13] | Transforms values using chart-supplied migration definitions. | Reuse maintainer-owned rules where available. Automatic values migration is already an existing capability. |
| Strong coding assistant plus supplied docs | Can be tested on exactly the same inputs. | Mandatory baseline; generic prompting may be sufficient. No comparison has run yet. |

Plural publicly lists a Pro platform starting at $450/month for one cluster, with additional cluster pricing [14]. That is an adjacent category's advertised price, not evidence of transactions or a valid price for our smaller feature. Do not anchor our pricing to it or copy its advertised savings.

## Revised product hypothesis

Build a portable CLI/CI check that produces a migration review artifact for an existing update PR. Its candidate customer is a platform consultancy or team reviewing repeated changes across repositories without wanting another management platform. That preference is a hypothesis, not a discovered customer fact.

The report should preserve:

1. Exact chart archive/digest, application image identity and relevant configuration scope.
2. Version-specific documentation provenance and reviewed requirement identity.
3. The source and age of evidence used for each applicability/configuration decision.
4. Missing external facts, unsupported scope and conflicting sources.
5. A clear distinction between a configuration match and runtime verification.

Begin with one family of migration requirements whose evidence can be collected cheaply. Do not claim support for every chart, automatic safe upgrades, autonomous remediation or a fleet control plane. Check whether an existing tool already covers each proposed rule before implementing it.

The strongest possible differentiator would be independently tested interpretation and evidence handling with low adoption effort. It is not presently established, and competitors may already provide equivalent behavior.

## AI's role must earn its cost

An open-weight model could extract candidate requirements from unfamiliar prose: applicability, necessary evidence, supported action and exact source. It should not execute commands, approve deployment, invent missing state or become its own sole evaluator.

Before adding more infrastructure, compare:

- Existing tooling and normal engineer review.
- Manual, chart-specific reviewed rules.
- A strong prompted model/coding assistant using identical source material.
- Candidate extraction plus deterministic checking and source review.

Count the whole task: gathering inputs, inspecting output, correcting false alarms and resolving unknowns. Record missed prerequisites, unsupported assertions, source accuracy, correct abstention, elapsed human effort, model usage, retries and actual billed cost. Independent chart families are required for a generalization claim. Public docs may have been seen during model training.

Qwen3-8B remains an evaluation candidate. No winner is selected. Provider access and pricing must be checked before model calls. Tinker training follows an observed extraction weakness and independent labeled material; eight smoke cases are not an adequate training strategy. If AI offers no useful improvement, remove it and reconsider the challenge fit instead of manufacturing an AI dependency.

## Commercial validation and economics

The next customer evidence must come from authorized real work. Proposed gate: five qualified reviewers across at least two teams, one historical or pending upgrade case, and an identifiable budget owner. These are research targets, not statistical proof. No outreach has been sent.

Use CUSTOMER_REVIEW_INTAKE.md to collect the last actual task, existing alternatives, review steps, effort and data constraints. Prefer the difficult recent upgrade and its artifacts over hypothetical survey questions. Ask whether the user would run another evaluation and who could authorize a paid pilot. Do not count a friendly review or star as purchase evidence.

Possible recurring value is maintained, tested rule coverage and integration into repeated reviews. Possible failure is bespoke research per customer. Charge for a bounded review service if the work remains bespoke; do not describe labor-intensive delivery as scalable software.

Measure contribution per review as realized revenue less model, compute, storage, retries, support and allocated coverage-maintenance cost. No sale price or margin is proposed before usage and buying evidence. Sponsor credits finance experiments temporarily; they do not establish sustainable costs. No payment processing is required for this investigation.

## Resource decisions after the investigation

- Use local Python and pinned Helm artifacts for evidence now. No hosting/database is needed to run these experiments.
- Backboard is conditional for actual open-model comparison. Account-level access and eligible credits are unverified. Keep private configuration local; public source extraction can be evaluated separately.
- Render and a redeemed .tech domain can host a useful demonstration once the local path and model contribution work. A real public report is their purpose; they are not required to validate demand.
- Tinker remains conditional on a useful training experiment and observed held-out improvement.
- Add tracing when there are actual inference/retry failures to diagnose. Do not add orchestration, browsers, multiple databases or duplicate hosting for prize count.

Week 3 remains an opportunity to demonstrate the experiment, not a reason to distort its commercial purpose. The currently implemented code still lacks essential open-source AI. It is not a complete qualifying submission. The final write-up must distinguish public reports, our rendered observations and any future runtime/model/customer results [15].

## Continue, narrow or stop

Continue now: obtain one authorized real case, implement artifact-backed fact collection, and run the model/manual-review comparison when access is available.

Narrow: if one recurring migration family is valuable but wider coverage is costly, ship that feature. If human investigation dominates, evaluate a paid engineering service.

Stop the platform thesis: if reviewers do not have repeated work; if a coding assistant/existing tool yields equivalent reviewed output with less effort; if missing state cannot be collected economically; if unsupported assurances persist; or if maintenance exceeds what buyers will fund.

International credibility would come from reproducible cases, measured limits and an artifact that other engineers find useful. We cannot promise attention from Microsoft, AWS or other companies, or infer that visibility produces revenue.

## Source list

1. https://github.com/external-secrets/external-secrets/issues/4662
2. https://github.com/external-secrets/external-secrets/issues/5478 — body and discussion reviewed.
3. https://github.com/external-secrets/external-secrets/issues/4816 — body and discussion reviewed.
4. https://github.com/prometheus-community/helm-charts/issues/4981 — body and discussion reviewed; linked fix not executed.
5. https://github.com/prometheus-community/helm-charts/issues/3792
6. https://github.com/prometheus-community/helm-charts/issues/7230 — body and available discussion reviewed.
7. https://github.com/kubernetes/kube-state-metrics/blob/v2.14.0/README.md — blob `0108cede906f11d049a07b3d095b622ec5a4d957`; Kong guide blob `893527759a66e5293aded6999f8c6879b634c6d6`: https://github.com/Kong/charts/blob/main/charts/kong/UPGRADE.md#2260
8. https://www.plural.sh/products/upgrade-management
9. https://docs.plural.sh/plural-features/k8s-upgrade-assistant/addon-compatibilities
10. https://kubegrade.com/
11. https://docs.renovatebot.com/modules/manager/helmv3/
12. https://github.com/databus23/helm-diff
13. https://github.com/OctopusDeployLabs/helm-migrate-values
14. https://www.plural.sh/pricing
15. https://dev.to/challenges/hacktoberfest-week3-2026-10-19

Primary source retrieval through the GitHub connector was used where browser retrieval failed. Blob hashes identify file bytes, not immutable commit refs. Lab chart archives have separately recorded SHA-256 values. Neither selected issue counts nor vendor claims constitute an independently measured market.
