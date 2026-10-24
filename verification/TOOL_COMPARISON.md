# Existing-tool comparison ; October 20, 2026

## Decision

Keep the standalone commercial platform at NO-GO. The experiment confirms a narrow semantic distinction, not a validated business or a competitive win. Keep the checker as a possible extension to an existing review workflow. Do not add hosting, more databases, sponsor SDKs or paid training now.

## Executed comparison

The input pair is the official Kong 2.25.0 and 2.26.0 chart archives, both with identical controlled values: proxy image 3.3.0, the bundled controller disabled, database off and PostgreSQL disabled. Archive hashes match the earlier publisher-index verification. A disabled controller's configured tag is not evidence about an external controller.

| Method | Actual observation | What it establishes |
| --- | --- | --- |
| Helm 3.12.3 `lint --strict` | Exit 0 for both extracted chart versions; no chart lint findings. Helm emitted file-permission diagnostics for `/dev/null`, the deliberately empty kubeconfig. | Both inputs passed this chart lint run. No application readiness or upgrade-path approval follows. |
| Previously executed selected-field diff | Readiness endpoint visibly changes from `/status` to `/status/ready`. | Normal comparison exposes the change. We cannot sell discovery of an invisible diff. The helm-diff plugin was not executed. |
| ShiftScope 0.4.0 Helm 4 readiness analyzer, pinned commit | Both charts produce the same four rule IDs: chart API v2, template composition, ignore semantics and values transforms. One is warning severity and three are informational. | The implemented analyzer reports Helm 4 migration concerns. Kong application-version conditions are outside its stated scope. This is not an accuracy failure. |
| Our existing artifact checker, target proxy-only render | UNKNOWN: external controller version and its separate relationship are missing. | Our human-authored rule identifies facts needed to decide this one documented condition. It does not demonstrate an affected live installation. |
| Our existing artifact checker, colocated-controller render | NOT_APPLICABLE for this particular separate-controller condition. | Selected local content excludes that condition; it does not certify the upgrade. |

The new commands and exact stdout/stderr are in `tool-comparison-results.json`. The existing selected-field diff and two checker reports remain in their original files. These are not simultaneous live-system measurements or a representative accuracy benchmark.

The official Kong guide explains that chart 2.26 changes readiness behavior and cannot infer a separately deployed controller's version. That missing cross-deployment context is the technical problem under investigation. A person reading the guide and supplying the relevant facts can also resolve it. This experiment did not establish that automation saves that person time.

## Scope and reproducibility

Run from the project directory, after obtaining the locked charts and Helm binary using the earlier experiment harness:

```bash
python3 verification/run_tool_comparison.py --shiftscope /path/to/shiftscope
```

Use ShiftScope commit `b67c4a8694749418f42385b2aa1b36ef1e4c48a0`, Python 3.12.14, Pydantic 2.14.0 and PyYAML 6.0.3 for the recorded environment. This run imported the inspected analyzer source directly; it did not install/run ShiftScope's CLI, AI, MCP, SARIF or GitHub Actions integrations. The parser reads chart defaults/templates, not our separate Helm values file. Findings about future Helm capabilities are tool output, not claims independently validated by this experiment.

Chart extraction used hash-locked archives, rejected links and special files, bounded member count/size and Python's data extraction filter. Helm ran offline lint only with an empty kubeconfig. There were no cluster connections or chart hooks executed. This is not an operating-system sandbox for arbitrary untrusted tools or charts. Historical charts and Helm are research inputs, not production version recommendations.

## What this changes

There is evidence of additional application-specific context beyond chart lint and a diff. There is no evidence yet of a defensible standalone product, current buyer urgency, better review outcomes or a sponsor-worthy AI core. Existing SDKs and conservative evidence reporting reduce the case for another framework.

The next justified test is one authorized current upgrade review with its actual reviewer. Start from the team's normal diff and migration-document process. Record total reviewer effort, false alarms, missing facts and whether our report changes an independently checked decision. Include time spent collecting extra evidence and correcting model output. Do not declare success merely because a rule reports a warning. If there is no useful net improvement, stop this direction. A usable result in one review still would not establish recurring demand or willingness to pay.

That evaluation needs an actual workflow and reviewer; none is present in the available evidence. No interview responses, buyer commitments or deployment outcomes were invented. The existing customer intake remains blank. No customer messages, external contributions or contest submissions were sent.

## Sources

- Kong guide: https://github.com/Kong/charts/blob/main/charts/kong/UPGRADE.md#2260 ; the original inspected source Git blob is recorded in checker reports.
- ShiftScope analyzer: https://github.com/thc1006/shiftscope/blob/b67c4a8694749418f42385b2aa1b36ef1e4c48a0/src/shiftscope/analyzers/helm4/analyzer.py
- ShiftScope parser and rules: the same pinned repository, `parser.py` and `rules.py` in that directory.
- All local chart identities, settings and prior renders: `experiment/artifact-lock.json` and `experiment/outputs/experiment-results.json`.
