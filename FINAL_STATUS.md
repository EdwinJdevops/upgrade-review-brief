> Release verification snapshot recorded before the owner requested the Chart Ledger branding change. Current deployed identity is available at /healthz. New branding checks are in verification/branding/.

# Final status

## 1. Time

Recorded 2026-10-25T23:02:24.773072+01:00 in Lagos. Official deadline: 07:59 Lagos, October 26. Internal freeze: 01:59 Lagos, October 26. Remaining at this observation: 8 h 56 min to the official deadline; 2 h 56 min to the freeze. The owner's one-hour closeout target is distinct from the official deadline.

Evidence: verification/closeout/final-clock.json and verification/phase0/official-web-fetch.json.

## 2. Phases

| Phase | Status | Revision and evidence |
| --- | --- | --- |
| 0 Baseline/rules | DONE | 86b9f0265e0a60414ed0df70cf05dc29b4f5450e; docs/SUBMISSION_CHECKLIST.md; verification/phase0/ |
| 1 Hygiene | DONE with conditional omissions | 168e1c887a75ab9c1edb9090d5a3783adc3e4f27; verification/phase1/. Apache-2.0 added. Docker omitted and remote description/topics not set. A later missing README link was corrected. |
| 2 Determinism | DONE with failed comparison and fallback | de6f883e55e78b9e08a9c894f02044d3fbad4434; verification/phase2/. Local repetition matched; GitHub scores differed. General determinism claim dropped. |
| 3 Render | PARTIAL | Application 3cc347f04f127ccc295645ffb7a3481573f0abe2 measured; final release a971584b9662f810aefc24b34c69d6366c9268c0. verification/phase3/live-closeout/ and verification/closeout/. Cold start and fresh Blueprint install NOT RUN. |
| 4 Backtest | NOT RUN | No labels commit or cases; verification/backtest/verdict.md. Minimum-case fallback not met. |
| 5 Reusable Action | NOT RUN | No reusable Action committed or executed. Existing release workflow succeeded but is not a reusable Action. No Action prize claim appears in the submission. |
| 6 Facts | DONE for the executed checks | SUBMISSION_FACTS.md, plus final receipts on the closeout verification branch. No unsupported benefit or accuracy claims. |
| 7 DEV draft | PARTIAL against the full directive | Clean and annotated drafts are committed at a971584b9662f810aefc24b34c69d6366c9268c0. Template/tags and measurement table are present. Requested full-set ranking thesis cannot be decided because Phase 4 is unfinished. Not published. |
| 8 Release | PARTIAL | Final deploy live, main/health match, clean-clone suite 103 tests, CI run 40237353226 success. Tag push FAILED; fresh mobile-width and saved screenshot checks incomplete. |

Measured readiness example: 20 successful serial requests, p50 10.300 s, p95 11.856 s. Range review: 10 successful serial requests, p50 19.403 s, p95 21.538 s. These include form GET and review POST. Concurrent bursts returned one success in each; one rejection for two clients and four rejections for five clients, with a visible retry message. Highest logged sampled inference RSS: 1075441664 bytes. These results do not establish production capacity.

## 3. Release identity

Main: a971584b9662f810aefc24b34c69d6366c9268c0.
Live /healthz: a971584b9662f810aefc24b34c69d6366c9268c0, HTTP 200, ready.
They match. Evidence: verification/closeout/release-health.json and release-deploy-live.json.

## 4. Remaining commands and manual checks

Exact existing verification commands and prerequisites are in verification/closeout/remaining-checks.md. For the current release:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python verification/verify_manifest_coverage.py --commit a971584b9662f810aefc24b34c69d6366c9268c0 --output verification/closeout/release-live-repeat.json
python verification/measure_render.py --expected-sha a971584b9662f810aefc24b34c69d6366c9268c0 --output-directory verification/phase3/release-repeat
```

The tag exists locally but its push failed. From an authenticated checkout containing that tag, retry exactly:

```bash
git push origin refs/tags/v0.1.0
```

No runnable command exists for the unfinished multi-chart benchmark or absent reusable Action. No Dockerfile exists, so an image build is not represented as an executable check. Cold restart and disposable Blueprint create/test/delete require capabilities unavailable through the connected operations. Fresh mobile/browser screenshot verification requires a working browser with viewport and file-capture support. These are not silently counted as passed.

Publication is deliberately unperformed. Review DEV_SUBMISSION_DRAFT.md and publish through the official Week 3 template with devchallenge and hf26challenge before the verified deadline. Code publication alone is not an entry. Personal entrant representations require the owner's truthful determination.

## 5. Deviations

See verification/closeout/deviations.md. The original Render phase was interrupted and exceeded its timebox. A closeout run was explicitly recorded. The benchmark and its minimum-case fallback were not achieved. The native Render build is the tested alternative to an unrun container build. Fresh-service installation, cold restart and fresh mobile capture are unrun. Historical failed checks are retained. The first clean-clone attempt used the wrong working directory; its failure and corrected run are retained. The tag push failed because terminal Git lacks authentication, and the connector exposes no tag-creation operation. No credentials were requested or exposed. Final deployment receipts are recorded on a separate verification branch so main stays at the measured release revision. No DEV post was published.

## 6. Ranked risks

1. Entry is not published by this execution. The owner must review and publish the draft, as the master directive requires draft-only delivery.
2. Ranking usefulness is unvalidated across charts. Do not claim superiority, saved reviewer time, incidents prevented or commercial validation. Complete the registered study after establishing its labels and case log.
3. The hosted service handles one inference at a time and rejects concurrent work. Keep this limitation visible; do not describe the demo as production capacity.
4. Cross-environment output hashes differed. Preserve the failure and dropped determinism claim.
5. Public tag, cold start, fresh Blueprint install and fresh mobile capture remain unfinished. They limit release verification. Docker is an omitted conditional deliverable; native deployment and actual hosted inference are verified.

## 7. Backtest table

| Required dataset | Evaluated cases | BGE rank/hit rates/MRR | BM25 rank/hit rates/MRR | Token overlap rank/hit rates/MRR |
| --- | --- | --- | --- | --- |
| Pre-registered multi-chart study | NOT RUN | Unavailable | Unavailable | Unavailable |

No cases were evaluated under the new protocol, so no wins, losses or exclusions can be manufactured. Earlier controlled Kong experiments remain historical evidence, not this study.

## 8. Backtest verdict, copied unedited

NOT RUN.

The pre-registered multi-chart backtest was not implemented or executed. There is no labels commit, case selection log, full-set ranking table or independently verified label set.

Whether BGE beats BM25 on top-3 over the required full set is unknown. No difference or per-chart result can be reported. Earlier controlled Kong experiments are not this benchmark and are not substituted for it.

The minimum-case fallback was not met. The one-hour closeout started with this work unfinished. Completing the deployment and recording actual service checks does not replace ranking validation.
