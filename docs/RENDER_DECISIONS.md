# Render decisions

These decisions describe the existing hosted service and its measured boundaries. They do not establish production capacity.

| Decision | Evidence | Alternative and reason |
| --- | --- | --- |
| Native Python build | Closeout deployment reached live at application revision 3cc347f04f127ccc295645ffb7a3481573f0abe2. See verification/closeout/deploy-live.json. | Docker image omitted because no local container builder is available and no image was built. The native build runs actual inference; it is not evidence about Docker. |
| 1c-2g instance | Live service settings in verification/closeout/render-service.json. Listed compute price: USD 25/month in verification/phase3/pricing.txt. | No smaller plan was tested. Do not claim optimal sizing or a capacity guarantee. Sampled inference RSS is recorded separately. |
| One inference at a time | Runtime lock in webapp.py. HTTP concurrency outcomes are preserved in verification/phase3/live-closeout/. | Parallel model inference was not measured. It was not enabled because it would change resource behavior without evidence. This service rejects competing work rather than maintaining a durable queue. |
| Load model at startup | wsgi.py constructs the verified LocalReranker before the application accepts reviews. | Lazy first-request initialization was not added. Cold-start latency was not measured, so no startup-time advantage is claimed. |
| HTTP readiness | /healthz returns model availability and deployed revision; configured on the service. See verification/closeout/render-service.json. | A TCP-only probe would not expose the same application-level readiness state. |
| Automatic deployment off | Live service setting and render.yaml. | Automatic deployment was not enabled during validation. Release changes are checked before an explicit deploy. |
| Blueprint retained without a Deploy button | render.yaml is available; fresh-service installation is NOT RUN. | A tested one-click installation is not advertised without creating, validating and removing a disposable service. |

The measurement command is:

```bash
python verification/measure_render.py --expected-sha 3cc347f04f127ccc295645ffb7a3481573f0abe2 --output-directory verification/phase3/live-closeout
```

Choose a new output directory for a repeat. The harness refuses to overwrite an existing measurement log. Successful serial percentiles exclude HTTP failures, which remain visible in the raw records. Measurements include client and network overhead. They are not model-only timings.

A rolling deployment duration is not a cold-start measurement. Per-process RSS samples are not total service memory. No extra paid service was created for this check.

## Observed hosted results

Readiness example: 20 attempts, no HTTP failures, p50 10.300 s and p95 11.856 s. Range review: 10 attempts, no HTTP failures, p50 19.403 s and p95 21.538 s. These values include the form GET and review POST from the measurement client, not just inference.

The concurrent bursts returned one HTTP 200 and one HTTP 429 for two clients, then one HTTP 200 and four HTTP 429 for five clients. Each rejection displayed a retry message. This supports documenting single-request capacity; it does not justify describing the demo as a multi-user production service.

The highest logged sampled Python-process RSS was 1075441664 bytes across the observed inference log records. Samples were taken every 10 ms. This observation does not establish total service memory, exact peak memory or safe parallel inference. The existing 1c-2g plan is retained; smaller plans were not measured.

Raw evidence: verification/phase3/live-closeout/summary.json, requests.jsonl and verification/closeout/runtime-memory-logs-final.json. The source ledger is SUBMISSION_FACTS.md.
