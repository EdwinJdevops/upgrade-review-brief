# Helm upgrade review — local evidence brief

Created October 20, 2026, during the published Week 3 entry period.

Browser-only start: read BROWSER_START.md. A pinned GitHub Actions workflow now prepares both fast tests and an optional CPU model demonstration. It has not yet run on GitHub because the target repository is not accessible. No WSL or user-side model installation is needed for that route. DEV_SUBMISSION_DRAFT.md follows the official template and still needs verified public code/demo links before publication.

Current decision: GO for the bounded hackathon build, with a working local model-ranked review brief. Commercial scaling remains unvalidated. Read HACKATHON_BUILD.md for the current scope and results; FINAL_VERIFICATION.md records the earlier checker/extraction assessment and its remaining commercial gates. The complete contest submission has not been published.

The current brief uses BAAI/bge-reranker-base locally to order source passages against a limited manifest diff. It retains every passage locator and never approves deployment. There are 45 passing code tests and an actual saved demo. A six-query author-defined relevance check gives six unique first-place expected matches versus five for a simple keyword baseline; this is a small feasibility result, not a customer or accuracy benchmark. Earlier Qwen configurations failed and are retained as negative evidence.

## Run the current brief

In a Python 3.12 virtual environment, install the exact executed package versions. The CPU PyTorch package comes from its official index:

```bash
python3 -m venv .brief-venv
source .brief-venv/bin/activate
python3 -m pip install torch==2.14.1+cpu --index-url https://download.pytorch.org/whl/cpu
python3 -m pip install transformers==4.57.1 PyYAML==6.0.3
python3 prepare_brief_source.py
python3 download_reranker.py .models/bge-reranker-base
python3 upgrade_brief.py brief-cases/kong-readiness.json --root . --model-dir .models/bge-reranker-base
```

The model download is approximately 1.1 GB plus tokenizer/config files. Weights are hash-verified and excluded from this archive. The tool makes no provider API calls after preparation. Runtime memory/speed on your laptop have not been verified. This local implementation does not use Render or Backboard yet.

Run the keyword comparison without Torch or model weights once PyYAML and the pinned demo source are available:

```bash
python3 upgrade_brief.py brief-cases/kong-readiness.json --root . --lexical-baseline
python3 -m unittest discover -s tests -v
```

Add `--format json` for machine-readable output. Reports print to stdout. `verification/demo-brief.json` and `verification/demo-brief.md` are the executed model demo. Field coverage is limited; read the report's unresolved section. Exit code zero means a brief was produced, never permission to deploy.

## Run the original assertion-only baseline without packages

Requires Python 3.12. In WSL Ubuntu, extract this directory, enter it, then run:

```bash
python3 upgrade_review.py examples/missing-controller.json
python3 upgrade_review.py examples/affected.json
```

The first example must abstain because the external controller version is missing. The second must flag the affected combination. The program never connects to a cluster or network and never changes input files. Exit code 0 means a report was produced, not that an upgrade passed. Exit code 2 means invalid input. Do not wire this prototype's exit status into a deployment approval gate.

## Run artifact checks and the test suite

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r experiment/requirements.txt
python3 review_artifacts.py artifact-cases/missing-controller.json --root . --now 2026-10-20T08:30:00Z
python3 -m unittest discover -s tests -v
```

The artifact CLI reads checksummed manifest files and extracts selected facts. It validates local content and asserted timestamp policy, not cluster identity or operational truth. See artifact-cases/README.md for replay limits and model-evaluation/README.md for the optional CPU model experiment.

## Scope

One human-authored rule derived from [Kong's guide, section 2.26.0](https://github.com/Kong/charts/blob/main/charts/kong/UPGRADE.md#2260): an older separately deployed controller and a newer proxy need a specific readiness configuration. See the source blob identity embedded in the report. The Git blob SHA identifies the retrieved file bytes, not a commit or chart package.

Accepted facts are normalized assertions, each with a nonempty reference string. References are not opened or authenticated. The positive result is now MATCHES_SUPPLIED_FACTS, replacing the earlier SATISFIED label; the negative result is CONTRADICTS_SUPPLIED_FACTS. Both describe assertions only. Neither establishes runtime readiness, actual backup status, chart provenance, evidence freshness, or general upgrade safety. Missing, malformed or unsupported evidence stays UNKNOWN.

The supported prototype scope is a stable source version below target chart 2.26.0. This does not validate the full upgrade path; exact source/target chart archives and render settings still need pinning. Other targets receive UNKNOWN rather than an unsupported clean bill. Historical versions are test cases, not a recommendation to deploy them.

## Commercial validation remains separate

Evaluate the narrow tool in an authorized current upgrade review against the team's normal process, including evidence collection and correction effort, before expanding it into a paid platform. The public historical replay cannot establish customer benefit. This requirement does not block completing the bounded hackathon entry. The generative extraction configurations failed; the new relevance model has a separate, executed and limited task. Hosting and sponsor categories must reflect actual useful integrations.
