# Upgrade review brief

**REVIEW REQUIRED**

One explicitly selected Deployment; image, HTTP probe path/port and read-only-root settings only

kong-2.25.0 → kong-2.26.0

## Focused manifest changes

- `containers/proxy/readinessProbe.httpGet.path`: `"/status"` → `"/status/ready"`

## Migration passages, ordered for review

All selected-section passages are retained. Scores are relative relevance, not confidence.

- **L101-L105** · score `4.337753` · `model-evaluation/sources/kong-guide.md`
  Source: https://github.com/Kong/charts/blob/main/charts/kong/UPGRADE.md#2260
  Read the recorded source lines; excerpt budget exhausted.
- **L89-L97** · score `0.323547` · `model-evaluation/sources/kong-guide.md`
  Source: https://github.com/Kong/charts/blob/main/charts/kong/UPGRADE.md#2260
  Excerpt preview: If you are using controller version
- **L113-L114** · score `-0.457179` · `model-evaluation/sources/kong-guide.md`
  Source: https://github.com/Kong/charts/blob/main/charts/kong/UPGRADE.md#2260
  Read the recorded source lines; excerpt budget exhausted.
- **L107-L111** · score `-0.899069` · `model-evaluation/sources/kong-guide.md`
  Source: https://github.com/Kong/charts/blob/main/charts/kong/UPGRADE.md#2260
  Read the recorded source lines; excerpt budget exhausted.
- **L99-L99** · score `-6.618974` · `model-evaluation/sources/kong-guide.md`
  Source: https://github.com/Kong/charts/blob/main/charts/kong/UPGRADE.md#2260
  Excerpt preview: This section goes under the 'gateway'

## Unresolved

- This brief does not verify a live cluster, a supported upgrade path or runtime readiness.
- Only the explicitly selected source section and Deployment fields were considered.
- Every source passage remains listed; relevance scores are neither applicability nor approval.
- No colocated ingress-controller appears in the selected Deployment. An external controller's version and relationship are not established by this input.

Mode: open_weight_reranker; model calls: 5; omitted passages: 0.
