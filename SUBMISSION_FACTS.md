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
| Original code licence decision | Apache-2.0, owner instructed and may overrule | docs/SUBMISSION_CHECKLIST.md and owner directive in conversation | Owner directive R9; licence file not yet added |
| Prior uncommitted work exists | Action, CLI and documentation changes precede this directive | verification/phase0/git-status.txt | git status --short |
| Source retrieval limitation | Direct DEV HTTP requests returned 403; web retrieval used instead | verification/phase0/source-fetch-errors.txt and official-web-fetch.json | urllib GET, then search_service.web_run |

| baseline-tests | 98 tests; exit 0 | verification/phase0/baseline-tests.txt | .venv/bin/python -m unittest discover -s tests -v |
| phase0-snapshot-tests | 100 tests; exit 0 | verification/phase0/phase0-snapshot-tests.txt | .venv/bin/python -m unittest discover -s tests -v |
| working-tests | 114 tests; exit 0 | verification/phase0/working-tests.txt | .venv/bin/python -m unittest discover -s tests -v |

## May claim

- The official deadline and internal schedule above.
- The baseline repository and Render settings above, clearly identified as baseline.
- Apache-2.0 is the owner's instructed licence decision, not an inferred permission grant. File addition remains pending.

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

Phases 1 through 8 are NOT RUN under this directive. Earlier work must not be relabelled as a newly executed phase. Phase 0 is in progress. Every subsequent measurement adds its command and raw output here.
