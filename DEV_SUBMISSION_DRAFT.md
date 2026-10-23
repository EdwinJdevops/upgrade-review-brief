---
title: "Upgrade Review Brief: let an open model prepare the migration reading"
published: false
tags: devchallenge, hf26challenge
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19).*

## What I Built

Upgrade Review Brief prepares the evidence for a Helm upgrade review. Give it two rendered Deployment manifests and an explicitly selected section of the migration guide. It reports changes in a limited set of fields, orders the source passages against those changes using an open-weight relevance model, and preserves source locations and unanswered questions.

The intended user is a platform engineer who has to collect that material before deciding how to upgrade. The automation covers preparation. It never gives permission to deploy.

The controlled example compares Kong chart 2.25.0 with 2.26.0. Both chart versions passed the executed strict Helm lint checks, while the rendered proxy readiness path changed. The review also needs context about a controller that may be deployed separately. A clean chart render alone does not supply that missing fact.

## Demo

The recorded local result is in `verification/demo-brief.md`, with machine-readable evidence in `verification/demo-brief.json`. The example identifies one readiness-path change, ranks five source passages and retains every passage locator. It explicitly reports that the external-controller context is unresolved.

[Open the successful GitHub Actions demonstration](https://github.com/EdwinJdevops/upgrade-review-brief/actions/runs/39942834494). The run summary contains the newly generated brief. Both jobs completed successfully: 45 tests passed, then the CPU job verified the source/model files and performed five model evaluations, retaining all passages. The workflow can be rerun from a browser without WSL or a model API key. This is a workflow execution demonstration; no screen recording is claimed.

## Code

[Source code and reproducible workflow](https://github.com/EdwinJdevops/upgrade-review-brief). The source and CI were published on October 23; the initial local implementation and recorded experiments began October 20 during the challenge window.

## How I Built It

Python performs the limited manifest comparison and binds the selected documentation to expected file identities. BAAI's `bge-reranker-base` scores the relationship between a description of the change and each source passage. PyTorch and Transformers run the model locally using hash-verified safetensors weights and built-in model classes.

The model produces relevance scores. It does not rewrite requirements or generate commands. Source line locations survive ranking. Configuration examples stay with their preceding conditions. Long passages are scored through overlapping token windows; inputs exceeding the bounded limits remain explicitly unscored.

Early experiments with a small generative model were unsuccessful. A separate relevance-label trial matched only three of six author-defined labels. I retained that negative result rather than describing it as a working feature.

The replacement reranker placed the expected passage uniquely first for six author-defined queries. A simple shared-token baseline did so for five, tying on the remaining query. This is a small feasibility check, not evidence of general superiority. The source and query cases are not independent or held out.

The GitHub Actions test job has 45 passing tests. They cover integrity checks, malformed inputs, limited-field privacy and preservation of review material. They do not prove application readiness, production safety or customer value. No total review-time saving has been measured.

## Why Does Open Innovation Matter?

The open weights let this inference step run in an operator-controlled environment after preparation. There is no provider API call in the ranking path, and a model API key is unnecessary. The model files and revision can be inspected and replaced through an explicit implementation change.

That is useful for deployment evidence: the tool can process its selected manifest fields without sending them to a hosted model API. Local execution still consumes compute and requires an initial model download. I have not established that it is cheaper or more accurate than every closed alternative.

## Attribution and scope

The migration guidance belongs to [Kong](https://github.com/Kong/charts/blob/main/charts/kong/UPGRADE.md#2260). The relevance model is [BAAI/bge-reranker-base](https://huggingface.co/BAAI/bge-reranker-base). PyTorch, Transformers, PyYAML, Helm and GitHub Actions provide supporting tooling. AI coding assistance was used in development.

Only selected fields in one Deployment and an explicitly selected migration section are covered. The project does not authenticate a live cluster or prove that every relevant migration warning has been collected. The project now has a successful GitHub Actions automation run. Other sponsor integrations have not been implemented.

## Prize Categories

I am entering Best Use of GitHub Copilot through the challenge description's explicit GitHub Actions option. Actions automates the code tests, verified model preparation, CPU inference and publication of the review brief to the run summary. GitHub Copilot itself was not used; this entry relies on the published Actions option, and category acceptance remains the organizers' decision.
