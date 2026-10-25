# Submission facts

Only claims with evidence belong in the submission. Historical documents are not current release verification.

| Claim | Value | Raw evidence | Producing command or operation |
| --- | --- | --- | --- |
| Official deadline | October 25, 2026, 23:59 PDT | verification/phase0/official-web-fetch.json | search_service.web_run open specific contest rules |
| Internal freeze | October 26, 2026, 00:59 UTC | verification/phase0/clock.json | Python datetime: deadline minus six hours |
| Internal submission target | October 26, 2026, 03:59 UTC | verification/phase0/clock.json | Python datetime: deadline minus three hours |
| Baseline main SHA | b2a6fc1145c32c8aeaf1e2d1c075fd4133e9cf42 | verification/phase0/github-main.json | GitHub GET /repos/EdwinJdevops/upgrade-review-brief/branches/main |
| Last known good deployment before Phase 0 | cc516074e570961088db688a677fca3be58729a0 | verification/phase0/render-deploys.json | Render list_deploys service srv-dbdl4ca9lscs73c4urq0 |
| Render health path | /healthz | verification/phase0/render-service.json | Render get_service service srv-dbdl4ca9lscs73c4urq0 |
| Automatic deployment setting | off | verification/phase0/render-service.json | Render get_service |
| Render commit environment variable | RENDER_GIT_COMMIT | verification/phase0/render-env.raw | urllib GET https://render.com/docs/environment-variables.md |
| Original code licence decision | Apache-2.0, owner instructed and may overrule | docs/SUBMISSION_CHECKLIST.md and owner directive in conversation | Owner directive R9; file added in Phase 1 workspace |
| Prior uncommitted work exists | Action, CLI and documentation changes precede this directive | verification/phase0/git-status.txt | git status --short |
| Source retrieval limitation | Direct DEV HTTP requests returned 403; web retrieval used instead | verification/phase0/source-fetch-errors.txt and official-web-fetch.json | urllib GET, then search_service.web_run |
| baseline-tests | 98 tests; exit 0 | verification/phase0/baseline-tests.txt | .venv/bin/python -m unittest discover -s tests -v |
| phase0-snapshot-tests | 100 tests; exit 0 | verification/phase0/phase0-snapshot-tests.txt | .venv/bin/python -m unittest discover -s tests -v |
| working-tests | 114 tests; exit 0 | verification/phase0/working-tests.txt | .venv/bin/python -m unittest discover -s tests -v |
| Phase 0 pushed SHA | 86b9f0265e0a60414ed0df70cf05dc29b4f5450e | verification/phase0/resume-main.json | GitHub GET branches/main |
| Phase 0 CI | run 40113113412 concluded success | verification/phase0/resume-ci.json | GitHub GET actions/runs?per_page=1 |
| Resume time and remaining time | see raw UTC values in resume-clock.json | verification/phase0/resume-clock.json | Python datetime UTC subtraction |
| Phase 0 deploy request | dep-dbeeb0ivcj2c73cmed60 accepted; terminal status recorded separately below | verification/phase0/deploy-trigger.json | Render trigger_deploy |
| Phase 0 health identity | git_sha equals 86b9f0265e0a60414ed0df70cf05dc29b4f5450e; HTTP 200 | verification/phase0/health-after.json | urllib GET /healthz and exact SHA assertion |
| Phase 0 live examples | Original, range and sanitised upload checks completed with real inference | verification/phase0/live-example-command.txt and live-example.json | .venv/bin/python verification/verify_manifest_coverage.py --commit 86b9f0265e0a60414ed0df70cf05dc29b4f5450e --output verification/phase0/live-example.json |
| Phase 0 deploy status | live | verification/phase0/deploy-live.json | Render get_deploy dep-dbeeb0ivcj2c73cmed60 |
| Apache-2.0 licence file | Downloaded official licence text; original code only | verification/phase1/license-fetch.json and local-links.json | urllib GET https://www.apache.org/licenses/LICENSE-2.0.txt; hashlib.sha256 LICENSE |
| Documentation links | 51 local file targets checked; no missing files | verification/phase1/local-links.json | Python pathlib existence check over README.md and docs/**/*.md |
| Quickstart comparison | Lexical report generated; not model inference | verification/phase1/quickstart-report.txt and quickstart-source.txt | .venv/bin/python prepare_brief_source.py; .venv/bin/python upgrade_brief.py brief-cases/kong-readiness.json --root . --lexical-baseline |
| Repo metadata proposal | Description and topics recorded; remote metadata NOT SET | verification/phase1/repository-metadata.json | Local JSON generation; no metadata-write capability exposed |
| Docker build | NOT RUN; Docker executable absent; no Dockerfile added | verification/phase0/tool-availability.json | shutil.which docker |
| Phase completion clock | see UTC and remaining seconds | verification/phase1/completion-clock.json | Python datetime UTC subtraction |
| Phase 1 pushed SHA | 168e1c887a75ab9c1edb9090d5a3783adc3e4f27 | verification/phase1/pushed-main.json | GitHub GET branches/main |
| Current progress clock | UTC, Lagos and remaining seconds recorded | verification/phase2/progress-clock.json | Python datetime UTC subtraction |
| Same-machine CLI repetition | 10 actual model CLI runs; all stripped hashes match: 59fe287518e29c37dc810687281a384bcbfd46fa7ec6bba37b19c405f7ec518e | verification/phase2/local/result.json and run-*.stdout.json | .venv/bin/python verification/check_determinism.py --runs 10 --model-dir .models/bge-reranker-base --output-directory verification/phase2/local |
| Determinism normalization | Removes named timing/timestamp fields only; retains scores and order | verification/phase2/normalization-test.txt | .venv/bin/python -m unittest discover -s tests -p test_determinism_normalization.py -v |
| GitHub hash comparison | MISMATCH; actual CLI exit 0, comparison script exit 1 | verification/phase2/github-attempt1/result.json and github-job-attempt1.log | GitHub run 40115767782; python verification/check_determinism.py --runs 1 --model-dir .models/bge-reranker-base --output-directory verification/phase2/github --expected-hash 59fe287518e29c37dc810687281a384bcbfd46fa7ec6bba37b19c405f7ec518e |
| General determinism claim | DROPPED under Phase 2 fallback; score floats differ across tested environments | verification/phase2/environment-comparison.json and verdict.md | Recursive comparison of normalized JSON artifacts |
| Dashboard access for cold restart and disposable service | NOT RUN beyond sign-in wall; no temporary paid service created | verification/phase3/dashboard-access.txt and access-limitations.json | cua.createBrowserTab authorized Render dashboard; current connector capability discovery |
| Public compute price | 1c-2g web compute listed at USD 25 per month; not a credit-balance statement | verification/phase3/pricing.txt and pricing.http.json | urllib GET https://render.com/pricing; HTML text extraction |
| Current Phase 3 clock and working test status | See raw timestamp and test summary | verification/phase3/status-clock.json and working-tests.txt | Python datetime UTC subtraction and .venv/bin/python -m unittest discover -s tests -v |
| Phase 3 instrumentation | RSS observation code and HTTP measurement harness written locally; not deployed or measured yet | memory_measurement.py and verification/measure_render.py | Local file creation; live execution pending |
| Phase 2 main SHA | de6f883e55e78b9e08a9c894f02044d3fbad4434 | verification/phase2/github-jobs-attempt1.json | GitHub GET workflow jobs |
| Phase 3 release snapshot tests | 103 tests; exit 0 | verification/phase3/snapshot-tests.txt | git archive HEAD, copy named instrumentation files, .venv/bin/python -m unittest discover -s tests -v |
| Deploy button | Removed; fresh-service test NOT RUN due sign-in and cleanup capability blocker | verification/phase3/deploy-button-fallback.json | README edit following access observation |

## May claim

- The official deadline and internal schedule above.
- The baseline repository and Render settings above, clearly identified as baseline.
- Apache-2.0 is the owner's instructed licence decision, not an inferred permission grant. File added in the Phase 1 workspace; publication is recorded separately.

## Must NOT claim

- User time saved, incidents prevented, independently verified labels, customers, revenue or commercial validation.
- Ranking accuracy beyond a completed, disclosed backtest. No new backtest has been run.
- Determinism, cross-environment reproducibility, latency percentiles, cold-start time or peak RSS before measuring them.
- A verified fresh-service Deploy button, Docker image build, Action execution, release tag or final clean-clone verification before running them.
- GitHub Copilot use, Backboard, Tinker or a .tech domain.
- That the latest workspace changes are committed, deployed or submission-ready.
- That a post was published. The owner expressly requests draft only.
- That arbitrary uploaded guide bytes were authenticated against their source URL.
- Guaranteed placement, prize eligibility certification or a guaranteed prize.

## Work not yet measured

Phases 0 and 1 completed, with the documented conditional Docker skip and metadata handoff. Phase 2 execution completed with the mismatch fallback and general determinism claim dropped. Phase 3 has instrumentation and a closeout deployment; measurements and final checks are recorded in the closeout ledger. Phase 4 is NOT RUN. Later phases remain partial until their outputs are recorded. Earlier work must not be relabelled as a newly executed phase. Every subsequent measurement adds its command and raw output here.

## Closeout observations, October 25

- Official rules rechecked: cutoff is October 25, 2026 at 23:59 Pacific daylight time, not one hour after this session began. Evidence: verification/closeout/clock.json and verification/phase0/official-web-fetch.json.
- The owner requested a one-hour delivery target. This is a work limit, not a revised official deadline.
- Docker, Podman and Buildah executables are absent. No Docker build failed because no Docker build was run. The alternative is the existing native Python Render build via render-build.sh. Evidence: verification/closeout/clock.json and render-service.json.
- Main is 3cc347f04f127ccc295645ffb7a3481573f0abe2. Live remains 86b9f0265e0a60414ed0df70cf05dc29b4f5450e before closeout deployment. Evidence: verification/closeout/github-main.json and render-deploys.json.
- Phase 3 deployment was interrupted previously. Instrumentation exists on main but has not yet been verified live. Benchmark, reusable Action and final annotated draft were not completed. They cannot be called passed.
- The Phase 4 labels and benchmark do not exist. There is no pre-registration commit or full-set ranking verdict. A one-hour closeout cannot be presented as the specified four-hour investigation.
- The cross-environment hash mismatch remains a recorded failure. The permitted fallback drops the general determinism claim; it does not turn the failed comparison into a pass.

- Closeout test suite: 103 tests, exit 0. Evidence: verification/closeout/tests.txt. Command: .venv/bin/python -m unittest discover -s tests -v. These tests use scorer doubles where documented and do not establish ranking accuracy.
- Local Playwright Chromium installation failed with a truncated ZIP archive. Evidence: verification/closeout/browser-install.txt. No local browser check is claimed from this attempt.

- Native Render deployment dep-dbf79v2vcj2c73f3946g reached live at revision 3cc347f04f127ccc295645ffb7a3481573f0abe2. Evidence: verification/closeout/deploy-live.json. Operation: Render get_deploy.
- Clean clone at revision 3cc347f04f127ccc295645ffb7a3481573f0abe2 passed 103 tests. Evidence: verification/closeout/clean-clone-tests.txt. The first attempt used the wrong working directory and failed; verification/closeout/clean-clone-tests-attempt1.txt is retained.
- Desktop browser example displayed the readiness path change, model report and both download events. Evidence: verification/closeout/browser-observations.json and CUA transcript. This observation is not attributed to the new revision; fresh mobile and screenshot checks remain NOT RUN.

## Closeout claim ledger

| ID | Claim and value | Evidence | Command |
| --- | --- | --- | --- |
| C01 | The selected Deployment scope is images, HTTP probe paths/ports and readOnlyRootFilesystem; broader resource changes are inventoried, not semantically assessed. | verification/closeout/implementation-contract.json; verification/closeout/live-functional.json | Python source capture; verification/verify_manifest_coverage.py |
| C02 | Actual hosted BAAI/bge-reranker-base execution uses pinned revision 2cfc18c9415c912f9d8155881c133215df768a70. Range example retains 16 passages and scores 32 windows. | verification/closeout/live-functional.json | .venv/bin/python verification/verify_manifest_coverage.py --commit 3cc347f04f127ccc295645ffb7a3481573f0abe2 --output verification/closeout/live-functional.json |
| C03 | The Kong packaged source links target commit b39300d09d6d70297dc437015d4a49e484b7b77d; uploaded URLs are not authenticated. | verification/closeout/live-functional.json; verification/closeout/implementation-contract.json | Same functional check and Python source capture |
| C04 | Model files are checked against the pinned identities; local_files_only and trust_remote_code=False are used at runtime. Input files are hashed; relevance scores do not approve upgrades or generate migration actions. | verification/closeout/implementation-contract.json; verification/closeout/live-functional.json | Python source capture; actual hosted report assertions |
| C05 | One native Python Render service uses 1c-2g, one worker, two threads, /healthz and automatic deploys off. The listed compute price is USD 25/month, not total billing. | verification/closeout/render-service.json; verification/phase3/pricing.txt | Render get_service; urllib pricing fetch |
| C06 | All reports require human review. Upload checks found the deliberate secret sentinels absent from the returned report; this is not a security audit. Hosted uploads reach the server; local inference calls no hosted model API. | verification/closeout/live-functional.json; verification/closeout/implementation-contract.json | Actual hosted functional assertions; Python source capture |
| C07 | Cross-environment normalized JSON differed in score floats. Local repetition matched on ten runs. No general byte-identical ranking-output claim is supported. | verification/phase2/local/result.json; verification/phase2/environment-comparison-summary.json; verification/phase2/verdict.md | verification/check_determinism.py and artifact comparison |
| C08 | The specified multi-chart backtest is NOT RUN; ranking advantage over BM25 is unknown. There is no reusable Action verified on a runner. | verification/closeout/backtest-inventory.json; verification/backtest/verdict.md | Git tree inspection and local file inventory |
| C09 | Apache-2.0 is the owner's instructed application licence decision. AI coding assistance was used; no Copilot use or unused sponsor integration is claimed. | LICENSE; THIRD_PARTY_NOTICES.md; owner directive and execution record | Licence fetch and file inspection |
| C10 | Cold start, fresh-service Blueprint installation, Docker image build and a fresh mobile browser check are NOT RUN. | verification/phase3/access-limitations.json; verification/closeout/browser-install.txt; verification/closeout/clock.json | Access discovery; tool availability; browser install attempt |
| C11 | Fresh local and clean-clone suites each ran 103 tests with exit 0 at application revision 3cc347f04f127ccc295645ffb7a3481573f0abe2. These are functional tests, not ranking accuracy. | verification/closeout/tests.txt; verification/closeout/clean-clone-tests.txt | .venv/bin/python -m unittest discover -s tests -v |
| C12 | The controlled example changes the readiness path from /status to /status/ready for Kong 2.25.0 to 2.26.0. No real customer incident or effort reduction has been established. | verification/closeout/browser-observations.json; experiment/outputs/kong-old-proxy-only.yaml; experiment/outputs/kong-new-proxy-only.yaml | Actual browser example; fresh functional check |

The submission may describe the implemented preparation workflow and its design purpose. It must not infer measured time saved, safer upgrades, general ranking superiority, commercial demand, production readiness, or expected placement.

- Repository is public and GitHub identifies the licence as Apache-2.0. Evidence: verification/closeout/repository.json. Operation: GitHub GET repository metadata.
- Latest workflow for application revision 3cc347f04f127ccc295645ffb7a3481573f0abe2 is cancelled, not passed. Cancellation cause is unverified. Evidence: verification/closeout/latest-ci.json. Operation: GitHub GET actions/runs?per_page=1.
- The native Render build completed and the new application revision is live; Docker image verification remains NOT RUN. Evidence: verification/closeout/deploy-live.json.
- Per-inference memory logs are now emitted by the deployed process. The partial sample summary is verification/closeout/memory-summary-partial.json; it is not the final peak or whole-service RSS.
- The new multi-chart backtest verdict is explicitly NOT RUN. It cannot support either a model-superiority thesis or a conclusion that BM25 won. Evidence: verification/backtest/verdict.md.

- Link check attempt 1 fetched all external README/post URLs with HTTP 200 but found a missing local evaluation/PROTOCOL.md target. The README link was changed to the existing model-evaluation/README.md history. The failure remains in verification/closeout/link-check-attempt1.json; a final local-link check is required.

## Completed hosted measurements

Command: `python verification/measure_render.py --expected-sha 3cc347f04f127ccc295645ffb7a3481573f0abe2 --output-directory verification/phase3/live-closeout`. Raw: verification/phase3/live-closeout/requests.jsonl; summary.json. Every attempt is retained. Successful serial percentiles use nearest rank. These are client/network/application measurements, not model-only latency.

| Claim | Value | Raw evidence | Command |
| --- | --- | --- | --- |
| Readiness example | 20 attempts; 0 failures; p50 10.300 s; p95 11.856 s | verification/phase3/live-closeout/summary.json and requests.jsonl | verification/measure_render.py command above |
| Range review | 10 attempts; 0 failures; p50 19.403 s; p95 21.538 s | verification/phase3/live-closeout/summary.json and requests.jsonl | verification/measure_render.py command above |
| Concurrent burst 2 | HTTP status counts: {"200": 1, "429": 1}; HTTP 429 responses display Another review is running. Try again when it finishes. | verification/phase3/live-closeout/summary.json and concurrent response HTML | verification/measure_render.py command above |
| Concurrent burst 5 | HTTP status counts: {"200": 1, "429": 4}; HTTP 429 responses display Another review is running. Try again when it finishes. | verification/phase3/live-closeout/summary.json and concurrent response HTML | verification/measure_render.py command above |
| Warm homepage | 10 successful requests; p50 4.654 s; p95 6.452 s | verification/phase3/live-closeout/summary.json | verification/measure_render.py command above |
| Highest logged sampled inference RSS | 1075441664 bytes; 35 log records; 10 ms samples; not total service memory | verification/closeout/runtime-memory-logs-final.json and memory-summary.json | Render list_logs text=inference_memory startTime=2026-10-25T21:33:23Z; Python maximum |
| Measurement revision | Health matched 3cc347f04f127ccc295645ffb7a3481573f0abe2 before and after the run | verification/phase3/live-closeout/health-before.json and health-after.json | verification/measure_render.py command above |
| Link checks | External targets returned HTTP 200; final local file targets all exist after correcting one missing link | verification/closeout/link-check-attempt1.json and local-links-final.json | Python urllib GET and pathlib.exists |

- Fresh desktop range browser observation at the measured release showed 32 model windows, 16 passages, REVIEW_REQUIRED and no horizontal overflow at 1363 by 936 CSS pixels. Evidence: verification/closeout/browser-range-observation.json and CUA transcript. This is not a fresh mobile-width check.
- Git history starts with a public initial commit dated October 23, 2026. Evidence: verification/closeout/git-history.txt. This is a repository-history observation, not a personal eligibility certification.

## Release confirmation ledger

| Claim | Value | Evidence | Command |
| --- | --- | --- | --- |
| Main release revision | a971584b9662f810aefc24b34c69d6366c9268c0 | verification/closeout/release-ci.json | GitHub branch update with expected SHA; GitHub GET actions/runs |
| Release clean clone | 103 tests, exit 0 | verification/closeout/release-clean-clone-tests.txt | Python unittest discover from clean checkout at a971584b9662f810aefc24b34c69d6366c9268c0 |
| Release CI | Run 40237353226 concluded success | verification/closeout/release-ci.json | GitHub GET actions/runs?per_page=1 |
| Tag publication | FAILED: terminal Git lacks authenticated push access; local tag exists only | verification/closeout/tag-push.txt | git tag v0.1.0 a971584b9662f810aefc24b34c69d6366c9268c0; git push origin refs/tags/v0.1.0 |
| Release confirmation clock | Exact UTC, Lagos, deadline and freeze values are in raw JSON | verification/closeout/final-clock.json | Python datetime and ZoneInfo arithmetic |

| Final deployment | dep-dbf7m8vb9u1s73btvprg reached live at a971584b9662f810aefc24b34c69d6366c9268c0 | verification/closeout/release-deploy-live.json | Render get_deploy |
| Final health identity | HTTP 200, ready; main and live both a971584b9662f810aefc24b34c69d6366c9268c0 | verification/closeout/release-health.json | urllib GET /healthz; git rev-parse HEAD; exact comparison |
| Final live functionality | Original, range and sanitised upload assertions completed with actual model inference | verification/closeout/release-live-functional.json and release-live-functional-command.txt | .venv/bin/python verification/verify_manifest_coverage.py --commit a971584b9662f810aefc24b34c69d6366c9268c0 --output verification/closeout/release-live-functional.json |
| Release runtime delta | No application runtime paths changed between the measured application and the final documentation/evidence commit | verification/closeout/release-runtime-diff.json | git diff --name-only 3cc347f04f127ccc295645ffb7a3481573f0abe2 a971584b9662f810aefc24b34c69d6366c9268c0 |
| Remote tests | Release CI tests job concluded success; raw runner log retained | verification/closeout/release-ci-jobs.json and release-ci-job.log | GitHub GET workflow jobs; fetch_workflow_job_logs 121301641827 |

Final claims remain limited to executed checks. The benchmark, reusable Action, container image, cold-start measurement, disposable Blueprint installation, fresh mobile-width check and published release tag remain unverified or unfinished. The DEV post is prepared, not published by this execution.

## Display branding update

The owner explicitly requested a displayed product rename and a logo above the README introduction, superseding the earlier presentation-only freeze restriction for this work. The displayed name is Chart Ledger. Repository name and live hostname are unchanged. No name exclusivity or trademark clearance is claimed. Evidence: verification/branding/branding-check.json; templates/base.html; static/chart-ledger-logo.svg.

The logo is an original SVG document/diff/source-link mark. It does not use a checkmark or imply upgrade approval. It is used in the application header and above the README introduction. The icon is also the favicon. Source and validation: static/chart-ledger-mark.svg, static/chart-ledger-logo.svg, verification/branding/branding-check.json.

Branding changes passed the full local suite: 103 tests, exit 0. Evidence: verification/branding/tests.txt. Command: .venv/bin/python -m unittest discover -s tests -v. This is not new ranking validation.

The DEV editor was opened through the browser and showed the sign-in form at https://dev.to/new. No account was signed in and no entry was published. Evidence: verification/branding/dev-editor-access.json and CUA transcript. The previous draft-only directive has been followed; the owner's latest request asks to proceed toward submission, which still needs DEV authentication.

Presentation decision: state the concrete review-preparation outcome, place a direct demo and quickstart near the top, and show measured evidence rather than unverified benefit promises. This is our application of the value/outcome and effort principles requested from $100M Offers, not a claim that the book establishes product demand or prize likelihood. Source consulted: Acquisition.com pricing/value checklist and official book page, retrieved in this session. No material from the book is copied into the product.

The final branding suite again ran 103 tests with exit 0 after the headline copy change. Evidence: verification/branding/tests-final.txt. The local Flask page and SVG asset check returned HTTP 200 using a scorer double; this is not an actual-model or responsive-browser check. Evidence: verification/branding/local-page.json. The SVG wordmark was rendered to a local preview and visually inspected before publication.
