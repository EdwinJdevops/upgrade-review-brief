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

Phases 0 and 1 completed, with the documented conditional Docker skip and metadata handoff. Phase 2 execution completed with the mismatch fallback and general determinism claim dropped. Phases 3 through 8 are NOT RUN under this directive. Earlier work must not be relabelled as a newly executed phase. Every subsequent measurement adds its command and raw output here.
