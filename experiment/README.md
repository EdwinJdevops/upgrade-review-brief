# Chart rendering experiment — October 20, 2026

This directory records nine executed render observations across two chart families. All configurations are controlled lab inputs. They are not customer deployments or production failures. No Kubernetes runtime, model inference, paid service or cloud deployment was exercised.

## Reproduce

Use Linux x86_64 / WSL2 Ubuntu with Python 3.12:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 run_render_experiment.py
```

Run from this experiment directory. The harness downloads the pinned Helm archive and chart packages if missing, verifies SHA-256, and extracts only the executable member from the Helm archive. The original chart downloads were also checked against each publisher's chart-index digest. The checksums establish byte identity against the recorded sources; no independent signature verification was performed. The deliverable omits the downloaded archives/binary; its first reproduction needs network access.

Helm 3.12.3 is a pinned historical lab dependency, not a recommendation for production installation. The binary is downloaded from the official Helm distribution host. Helm is not installed globally. Chart rendering uses explicit Kubernetes target versions and an empty kubeconfig; no hooks/post-renderers are executed. This harness is not an OS sandbox for arbitrary untrusted charts. It intentionally accepts only these reviewed lab inputs.

## Executed observations

| Case | Observed manifest property |
| --- | --- |
| Kong 2.25.0 proxy-only, proxy 3.3.0 | Probe path `/status`. |
| Kong 2.26.0, same proxy-only settings | Probe path `/status/ready`. |
| Kong 2.26.0 with explicit override | Probe path `/status`. |
| Kong 2.26.0 with colocated controller 2.10.4 | Chart falls back to `/status`. |
| Kong 2.26.0 with proxy 3.2.0 | Chart falls back to `/status`. |
| Kong 2.26.0 proxy-only with disabled-controller tag set to 2.11.0 | Probe remains `/status/ready`; that unused setting establishes no external controller fact. |
| kube-state-metrics chart 5.26.0 defaults | Image v2.13.0; `/readyz` on port 8080. |
| Same chart with image v2.14.0 | Image changes; probe remains `/readyz` on 8080. |
| Same override with self-monitoring enabled | Extra telemetry container port appears; readiness probe remains on 8080. |

The kube-state-metrics v2.14.0 README describes `/readyz` on the telemetry endpoint. We have not run the application to establish HTTP outcomes. The upstream issue links a fix and includes a later configuration counterexample; this experiment does not validate a universal remediation.

The assertions deliberately concern the rendered properties above, including properties associated with reported failures. “PASS” means the observation matched its documented expectation; it does not mean a deployment passed a health check.

## Files

- `artifact-lock.json`: source URLs, archive sizes and SHA-256 values.
- `source-records.json`: identities of documentation files; blob IDs are not commits.
- `public-evidence-ledger.json`: six selected upstream records, with disputed causes and limits retained.
- `outputs/experiment-results.json`: canonical nine-case result, command arguments and artifact hashes.
- `outputs/kong-*.yaml`, `outputs/ksm-*.yaml`: generated manifests. No customer secrets are present; generated names/settings are lab fixtures.
- `outputs/plain-diff-baseline.txt`: plain comparison of selected fields. It demonstrates that the changed fields are visible without a model. It is not a run of the helm-diff plugin.

Earlier exploratory output names, the large downloaded binary and historical indexes are excluded from the deliverable. The harness and lock allow the binary to be obtained again. Runtime behavior, model quality, useful review-time savings, competitor coverage and willingness to pay remain unmeasured.
