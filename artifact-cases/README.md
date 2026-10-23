# Artifact replay cases

These cases reference actual chart-render outputs from the lab experiment. They are not live cluster captures or customer configurations. `captured_at` is a synthetic fixture timestamp for deterministic replay with `--now 2026-10-20T08:30:00Z`; it is not an authenticated collection timestamp.

From the project directory, after installing `PyYAML==6.0.3`:

```bash
python3 review_artifacts.py artifact-cases/missing-controller.json --root . --now 2026-10-20T08:30:00Z
python3 review_artifacts.py artifact-cases/colocated-controller.json --root . --now 2026-10-20T08:30:00Z
```

The first report preserves UNKNOWN because external-controller state is absent. The second excludes this specific separate-controller condition; it is not approval of an upgrade.

The default 24-hour age limit is a prototype policy, not a validated freshness guarantee. Timestamps and expected hashes are caller assertions. Recomputing a checksum for fabricated content does not authenticate that content. Exit 0 means evidence processing produced a report; exit 2 means evidence or input was rejected. Neither is permission to deploy.
