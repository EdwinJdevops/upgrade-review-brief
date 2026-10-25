# Upgrade Review Brief

Helm upgrade reviewers must connect rendered Deployment changes to migration instructions.

![Example review report](docs/demo/report-desktop.png)

| Measurement | Result | Evidence |
| --- | --- | --- |
| Fresh unit suite and clean-clone suite | 103 tests each, exit 0 at application revision `3cc347f` | [Raw outputs](verification/closeout/) |
| Hosted readiness example | 20/20 HTTP 200; end-to-end p50 10.300 s, p95 11.856 s | [Raw HTTP run](verification/phase3/live-closeout/summary.json) |
| Hosted range review | 10/10 HTTP 200; end-to-end p50 19.403 s, p95 21.538 s | [Every attempt](verification/phase3/live-closeout/requests.jsonl) |
| Concurrent range requests | Bursts of 2 and 5: one completes in each; others receive HTTP 429 with a retry message | [Responses retained](verification/phase3/live-closeout/summary.json) |
| Actual hosted inference | Original example, range review and sanitised upload checked | [Functional check](verification/closeout/live-functional.json) |
| Same-machine CLI repetition | Matching normalized hashes on ten runs of the fixed example | [Raw repetition](verification/phase2/local/result.json) |
| Cross-environment hash comparison | FAILED: score floats differ; general determinism claim dropped | [Failure retained](verification/phase2/verdict.md) |
| Multi-chart ranking backtest | NOT RUN; model advantage over BM25 unknown | [Verdict](verification/backtest/verdict.md) |
| Container image build | NOT RUN; deployment uses native Python on Render | [Submission facts](SUBMISSION_FACTS.md) |

## Quickstart

Run from the repository root with Python installed. This comparison command uses no model; model setup is documented separately.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-web.txt
python prepare_brief_source.py
python upgrade_brief.py brief-cases/kong-readiness.json --root . --lexical-baseline
```

Fresh-service Blueprint verification is blocked by dashboard sign-in and unavailable connector cleanup operations. The Deploy button is omitted until that check is completed. The existing hosted service was created separately from the Blueprint.

## Scope and limits

The brief compares one selected Deployment's container images, HTTP probe paths/ports and read-only-root setting, then presents guide passages for human review. Other manifest edits are inventoried but are not semantically validated. Uploaded source URLs are not fetched or authenticated during a review. The public demo receives uploads on its server; use sanitised inputs. No report approves an upgrade or applies changes. User effort saved and commercial demand have not been measured.

## Documentation

- [Live application](https://upgrade-review-brief.onrender.com) and [recorded demonstration](docs/demo/browser-demo.mp4)
- [Submission facts](SUBMISSION_FACTS.md) and [official requirements checklist](docs/SUBMISSION_CHECKLIST.md)
- [Deployment and model setup](RENDER_DEPLOYMENT.md)
- [Evidence history](docs/EVIDENCE.md)
- [Known weaknesses](docs/KNOWN_WEAKNESSES.md)
- [Product decisions](docs/PRODUCT_EVOLUTION.md) and [earlier model experiments](model-evaluation/README.md)
- [Third-party notices](THIRD_PARTY_NOTICES.md) and [Apache-2.0 licence](LICENSE)

Apache-2.0 is the owner's instructed licence decision. Third-party licences remain separate. The DEV draft is prepared for owner review; it has not been published by this execution.
