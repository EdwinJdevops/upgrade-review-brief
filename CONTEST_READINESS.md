# Week 3 readiness audit — October 23, 2026

This is a working research prototype. It is not a submitted entry, a certified upgrade checker or a validated commercial platform.

## Product and theme

Upgrade Review Brief assembles a limited manifest diff, relevant migration reading and unresolved questions for a platform engineer. It automates preparation for an upgrade review. It does not perform or approve the upgrade.

The Week 3 theme is **Slow and Steady**: save effort with open-source AI at the core. The BAAI BGE open-weight relevance model has a real runtime role in ordering the reading. The browser route requires the model and never quietly substitutes keyword ranking. Whether the result is sufficiently compelling and competitive is the judges' decision. End-to-end reviewer time saved has not been measured.

## Requirements and present evidence

| Requirement | Status | Evidence or remaining action |
|---|---|---|
| New project in the entry period | Consistent with available records | Local implementation records date from October 20; GitHub reports repository creation on October 23. Entry period began October 19 at 09:00 PDT. Do not claim older work as new. |
| Essential open-source AI | Implemented | Pinned BAAI/bge-reranker-base weights, local CPU inference, source-preserving relevance ranking. Successful earlier CLI model run is linked in README. |
| Slow and Steady theme | Addressed by design | Automates manifest comparison and assembly/order of migration reading. User benefit and time savings still need independent evaluation. |
| Working demo: deployed link or video | Video recorded | docs/demo/browser-demo.mp4 records the actual browser interface running real CPU inference locally. Desktop/mobile uploads and downloads were checked. Render deployment is still pending. |
| Public code link | Available | https://github.com/EdwinJdevops/upgrade-review-brief |
| English DEV post using template and tags | Draft only | DEV_SUBMISSION_DRAFT.md; not published. Required tags: devchallenge, hf26challenge. |
| Explain why openness matters | Drafted | Inspectable/pinned weights and execution without a hosted model API; hosted browser mode still sends files to its server. |
| Credit substantial prior work | Recorded | THIRD_PARTY_NOTICES.md and draft attribution. Retain upstream notices and license obligations. |
| One entry per participant/team | No submission made here | Publish one final entry; credit all team members, maximum four. |
| Participant eligibility | Personal requirement | General rules require an eligible adult DEV member in good standing; entering constitutes acceptance of the official rules. Nigeria is not in the current listed excluded jurisdictions; this is not a determination of every personal/legal eligibility condition. |
| Post-deadline changes | Future obligation | Mark commits made after the entry deadline in README. |

Deadline: **October 25, 2026, 23:59 PDT**, equivalent to **October 26, 2026, 07:59 Africa/Lagos**. Publishing code alone does not submit the entry.

## Sponsor decisions

| Resource | Decision | Qualification boundary |
|---|---|---|
| Render | Implement browser service; deployment pending connection | Actual running AI runtime is needed before claiming Best Use of Render. Configuration alone is insufficient. Account credits, costs and deployed resource fit remain unverified. |
| .tech domain | Add after deployment if the event domain is actually claimed | Need the claimed domain, DNS access, live resolution/TLS and its link in the article. No domain has been registered or configured here. |
| Backboard | Do not add to this iteration | Existing local inference needs neither provider routing nor assistant memory. No use or category qualification is claimed. |
| Tinker | Do not add to this iteration | No task dataset, fine-tuning run or credible improvement over a baseline has been established. Calling a model or redeeming credits would not qualify. |
| GitHub category | Existing published Actions option is relevant | The challenge explicitly includes project automation with Actions under Best Use of GitHub Copilot. Actions was used; Copilot itself was not. Judges determine acceptance. |

One entry may identify multiple categories it meaningfully qualifies for, but **a participant can win at most one prize in this contest**. Sponsor tools are optional for the overall prize. No award or numerical chance of winning is established.

## Submission sequence

1. Completed locally: verify real model execution through the browser, retain evidence and record the demo. See verification/web-browser-2026-10-23.json and docs/demo/browser-demo.mp4.
2. Deploy on Render after connection and credit/compute review; test health, example, upload and report downloads at the public URL. If deployment is not available, prepare a genuine video demonstration instead.
3. Add the event-claimed .tech domain if access is available; verify DNS and HTTPS before listing the category.
4. Finish the article around the demonstrated behavior, measured results and limitations. Add the live demo/video and only actual sponsor categories.
5. Publish one DEV submission before the deadline and verify it appears among the challenge entries.

## Continuing after the contest

The reusable foundation is the separate comparison/ranking engine and browser adapter. Commercial expansion is unvalidated. The next evidence needed is real engineers reviewing their own changes, observed preparation effort, missed prerequisites, repeat usage and willingness to pay. More integrations or benchmark claims cannot substitute for that evidence.

## Official sources

- Challenge: https://dev.to/challenges/hacktoberfest-week3-2026-10-19
- Contest-specific rules: https://dev.to/page/hacktoberfest-week3-2026-10-19-contest-rules
- General rules: https://dev.to/page/official-hackathon-rules
- Render deployment fields: https://render.com/docs/blueprint-spec
- Render custom domains: https://render.com/docs/custom-domains
