---
title: "Upgrade Review Brief: less digging before a Helm upgrade"
published: false
tags: devchallenge, hf26challenge
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19).*

## What I Built

A Helm chart can render cleanly while leaving an important upgrade question unanswered.

In my controlled example, Kong chart 2.25.0 and 2.26.0 both passed strict Helm lint checks. The rendered proxy readiness path still changed from `/status` to `/status/ready`. Understanding that change means reading the migration guide and knowing about a controller that may run in a separate Deployment. The proxy manifest does not establish that controller's version.

Upgrade Review Brief prepares that reading for a platform engineer. Give it the current and proposed rendered manifests, select a Deployment, and supply a section of the migration guide. It produces the selected-field diff, uses an open-weight model to order relevant source passages, and keeps unresolved questions visible.

The part I want to automate is collecting and arranging the evidence before the review. The decision remains with the engineer.

## Demo

[Watch the browser demonstration](https://github.com/EdwinJdevops/upgrade-review-brief/blob/main/docs/demo/browser-demo.mp4). This is a genuine recording of the local application running CPU inference, not a deployed Render instance or a simulated model response.

![Browser interface for the controlled example and sanitized file uploads](https://raw.githubusercontent.com/EdwinJdevops/upgrade-review-brief/main/docs/demo/home-desktop.png)

The included example identifies the readiness-path change, evaluates five model windows and retains all five migration passages with their source line locations. The report explicitly leaves the external-controller context unresolved. JSON and Markdown downloads preserve the result for review.

![Actual review result with a focused diff and source-linked migration reading](https://raw.githubusercontent.com/EdwinJdevops/upgrade-review-brief/main/docs/demo/report-desktop.png)

The browser checks also exercised sanitized uploads at a mobile viewport, checked both downloads and found no page JavaScript errors or horizontal overflow at the tested width. The [recorded evidence](https://github.com/EdwinJdevops/upgrade-review-brief/blob/main/verification/web-browser-2026-10-23.json) includes the model revision and actual report. These checks are specific to the tested scenario and viewports.

An [earlier GitHub Actions demonstration](https://github.com/EdwinJdevops/upgrade-review-brief/actions/runs/39942834494) separately executed the CLI with the same pinned model. The browser service is prepared for Render; no live deployment or Render category qualification is claimed yet.

## Code

[Source code, tests and reproducible workflow](https://github.com/EdwinJdevops/upgrade-review-brief).

Local implementation began October 20, during the challenge window. The public repository was created October 23. The repository includes negative experiments and the boundaries of the implemented feature.

## How I Built It

Python compares a limited set of fields in one explicitly selected Deployment: container images, HTTP probe paths and ports, and read-only-root settings. It creates a focused description of the changes without including environment values, headers, Secrets or the entire manifest in the model query.

BAAI's `bge-reranker-base`, running through PyTorch and Transformers, scores the relationship between that description and each migration passage. It produces relative relevance scores, not generated migration instructions. The system preserves every selected-section passage locator, including material that exceeds scoring limits.

Configuration examples stay with their preceding conditions. Long passages use overlapping token windows. The browser adapter allows at most 32 model windows per request and one inference request at a time. Files are processed in a temporary directory and removed afterward. Supplied source URLs are recorded rather than fetched; supplied filenames never become server paths. Inputs are identified by hashes, which establish byte correspondence rather than publisher authenticity.

The test suite now has 58 passing tests covering these boundaries and the browser adapter. Browser testing found a multipart size limit that rejected the supplied guide; I corrected it and added a regression test. I also moved excerpt allocation after ranking so the most relevant passage receives a preview rather than losing it to earlier source order.

Earlier generative-model experiments were unsuccessful. A separate relevance-label trial matched only three of six author-defined labels. I retained those results. The replacement reranker placed the expected passage uniquely first for six author-defined queries; a shared-token baseline did so for five and tied on the remaining one. That small, non-independent check established feasibility for this prototype. It does not establish general accuracy or superiority over existing tools.

## Why Does Open Innovation Matter?

The ranking step runs from inspectable, pinned open weights. It needs no model API key and can execute in an operator-controlled environment after the initial download. The application uses built-in model classes, verified safetensors files and an explicit revision rather than downloading remote model code at request time.

The browser version makes a different hosting trade-off from running the CLI yourself: uploaded files go to the application server, although that server calls no hosted model API. Running it on someone else's infrastructure is not the same as keeping files on your own laptop.

## Lazy Payoff

The application assembles the selected diff, ordered reading and unanswered questions in one exportable brief. That is the work it currently automates. I have not measured total engineer time saved, production readiness or customer demand.

Only one Deployment, selected fields and an explicitly chosen documentation section are covered. Other resources and skipped releases can contain essential migration requirements. A successful report always says **REVIEW REQUIRED**; it never authorizes a deployment.

## Attribution

The migration guidance and chart belong to [Kong](https://github.com/Kong/charts/blob/main/charts/kong/UPGRADE.md#2260). The model is [BAAI/bge-reranker-base](https://huggingface.co/BAAI/bge-reranker-base). PyTorch, Transformers, PyYAML, Flask, Jinja, Gunicorn, Helm and GitHub Actions provide supporting tools. Playwright was used to test and record the browser. AI coding assistance was used in development. Further source records are in [THIRD_PARTY_NOTICES.md](https://github.com/EdwinJdevops/upgrade-review-brief/blob/main/THIRD_PARTY_NOTICES.md).

## Prize Categories

I am entering **Best Use of GitHub Copilot** through the challenge description's explicit GitHub Actions option. Actions automates tests, verified model preparation, CPU inference and publication of the review brief to the run summary. The workflow also includes an actual-model browser-route check when its optional model job is requested.

GitHub Copilot itself was not used. This entry relies on the published Actions option; category acceptance remains the organizers' decision. Render and the event .tech domain will only be listed if they are actually deployed and verified before submission.
