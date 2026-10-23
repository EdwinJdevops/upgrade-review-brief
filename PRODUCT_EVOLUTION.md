# Version-range migration review — October 23, 2026

This implementation addresses two measured limitations of the original reading brief: users had to identify a section themselves, and all changes shared one reading order. It keeps the engine local/CI-capable and the hosted deployment within the existing single-instance configuration.

## What changed

- **Automatic section selection:** stable, increasing chart-name-X.Y.Z labels select level-two release headings satisfying `from < release <= to`. Unversioned level-two sections are retained except the table of contents; the preamble outside those sections is explicitly excluded in the ledger and requires separate review. A ledger shows every included/excluded heading. Prerelease labels, different chart identities, downgrades and ambiguous headings require an explicit section instead. This identifies supplied headings, not complete or applicable migration history.
- **Reading by change:** up to six changed fields receive independent queries. The guide passages are scored in interleaved order under one shared 32-window budget, so the first change cannot consume the entire budget. Source material remains listed when scoring runs out. Additional changes remain in the diff and are marked as lacking a dedicated query.
- **Conservative output:** scores from separate queries are never averaged or compared. The report groups source readings by the field they concern, preserves source hashes/line locations and records incomplete coverage. GitHub blob source links point at the recorded lines; a supplied URL still does not authenticate those bytes. The model does not extract executable actions or decide applicability.
- **Direct-file CLI:** `review_change.py` accepts the before/after manifests and guide, calculates input hashes and prepares the same plan. Users no longer need to author case JSON. It reads files locally, performs no source URL fetching, chart execution or cluster writes, and can produce JSON for an existing CI pipeline.
- **Browser:** blank section means automatic selection; an explicit section preserves the previous behavior. The new controlled range example and the original example remain separately available.

## Actual experiment and limitations

Official Kong chart archives 2.18.0 and 2.26.0 were rendered with the same controlled values, using the previously verified Helm executable and an empty kubeconfig. Both archive hashes were checked; the 2.18 archive digest was retrieved from the publisher index. The actual rendered changes are an unspecified read-only-root setting becoming true and `/status` becoming `/status/ready`. This is a historical configuration experiment, not evidence of an affected customer or live upgrade.

The supplied guide contributes 16 passages from release sections 2.19.0 and 2.26.0 plus unversioned guidance. The model evaluates 32 windows for two independent questions. All passages are retained and all query–passage pairs are scored in this case.

Before running inference, the evaluation froze the two author-labeled prerequisite passages, candidate hashes, combined baseline query and four-slot reading budget. Results:

| Method | Prerequisite passages surfaced in four reading slots |
|---|---|
| Per-change BGE, two readings per field | Both: filesystem condition and readiness condition |
| Per-change keyword overlap, same queries/candidates | Readiness condition; filesystem condition outside its first two |
| Combined BGE query, four readings total | Both |
| Exploratory BM25, two readings per field | Readiness condition; filesystem condition outside its first two |

The useful observed AI contribution here is bringing the filesystem condition into the first two readings for its field, where keyword matching ranked it seventh. The separate questions improve organization; this experiment does not show that decomposition outperforms the combined model at the same total reading budget. The original single-section demo still chooses the same first passage with and without the model. Both results remain published.

A BM25 comparison with fixed conventional parameters (k1=1.2, b=0.75) also surfaced one of the two conditions in its first two readings per field. It was added after seeing the original comparison and is explicitly exploratory, not a new independent test. See verification/range-bm25-posthoc.json and its replay script. These are author labels over one controlled chart family and public documentation. They are not independent accuracy estimates, total-review time savings, applicability classification or incident-prevention results. No training run or model switch was performed to obtain a preferred result. BGE remains the purpose-trained relevance model; the change is the review workflow around it.

## Verification and reproduction

- 68 unit tests, including numeric version boundaries, duplicate/fenced headings, source identity, privacy of unselected manifest fields, budget exhaustion, extra-change coverage and browser behavior. Network-free execution is checked with the guide directory temporarily absent; scorer doubles do not measure model quality.
- Actual-model local browser checks passed at desktop 1440×1000 and mobile 390×844: range example, automatic selection from uploads, two change queries, 16 retained passages, 32 windows, both downloads, no observed horizontal overflow or page JavaScript errors.
- Single local request processing was about eight seconds, excluding initial model loading and human preparation. It is not a throughput, customer-effort or Render performance result.

```bash
python prepare_brief_source.py
python verification/prepare_range_case.py
RERANKER_CPU_THREADS=1 python verification/evaluate_range_review.py
python -m unittest discover -s tests -q
RERANKER_CPU_THREADS=1 python verification/verify_range_local.py
```

`prepare_range_case.py` downloads pinned official historical archives if missing and uses the locked Helm executable. It is an operator-controlled lab harness, not a sandbox for arbitrary customer charts. `evaluate_range_review.py` refuses to overwrite a changed frozen contract; keep original evidence when creating a different experiment.

Evidence: verification/range-render-2026-10-23.json, verification/range-evaluation-contract.json, verification/range-evaluation-results.json, verification/range-local-browser-2026-10-23.json and verification/range-tests-2026-10-23.json. The final deployed revision, successful 68-test CI run, full public-browser checks and targeted metadata/inference follow-up are linked in verification/render-range-release-2026-10-23.json. Local success alone was not treated as deployment success.

## Commercial work still required

The workflow is more useful to test, but no customer outcome or purchase has appeared by writing this code. The next authorized historical review must measure input gathering, reading, corrections and missed prerequisites against that team's normal tools. Expand supported formats/fields only against observed work. Authentication, tenant isolation, retention controls and cost measurements precede private multi-user pilots. Original application licensing remains an owner decision; upstream licenses are separate.

The commercial hypothesis remains an evidence-preparation feature within repeated upgrade reviews. Paid maintenance of trustworthy coverage and workflow integration may be valuable, but neither paid demand nor sustainable margins is established. Existing tools and strong assistants remain comparison arms. No additional hosting, training, database or orchestration service was added for prize count.

## Subsequent coverage-boundary update

The full supplied renders now receive a deterministic resource inventory, separate from model reading. The existing Kong range has three modified resources with outside-scope edits (Deployment, Service, ServiceAccount), rather than only its two focused field changes. This makes an existing limitation visible; no additional migration conditions are inferred. Fixed categories detect edits in the selected Deployment's other settings without exporting their contents or arbitrary key names. Resource identifiers are included.

Identity is literal API version/kind/namespace/name, with no discovery, defaulting or conversion. Mapping/resource-document order and YAML comments are ignored; sequence order and type changes can count. Duplicate identities, unexpanded List wrappers, non-string mapping keys and non-JSON scalars are rejected before model execution. Invalid documents are not silently omitted. The source-ranking limits and model remain unchanged.

The direct CLI accepts `--fail-on-unreviewed-changes`: emit the normal report, then exit 3 on outside-scope edits, 0 otherwise, or 2 on input/review failure. Every successful report still says REVIEW_REQUIRED. This is a coverage guard, not upgrade approval or a policy/severity engine. The hosted range-example provenance label was also corrected to packaged_demo.

85 unit tests pass, including CLI subprocess exits, changed Secrets with withheld payloads/keys, unsupported Deployment settings, init containers, probe timing/actions, API-version/namespace changes, YAML type changes, duplicate identities, browser output redaction and pre-inference validation. These are software tests using scorer doubles. `verification/verify_manifest_coverage.py` separately exercises real hosted inference and the new inventory with sanitized fixtures; its execution result must be read separately rather than assumed from the script's presence.
