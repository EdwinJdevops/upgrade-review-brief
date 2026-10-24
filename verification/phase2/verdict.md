# Determinism verdict

The general determinism claim is dropped.

Ten actual CLI runs on the local machine produced the same normalized JSON hash. The GitHub runner's actual CLI output produced a different hash. The comparison job exited 1. Both the failed comparison and its artifacts are retained.

The differences are score and window-score float values. Passage order, input hashes and the other normalized fields did not differ in this comparison. The largest observed score difference is recorded in environment-comparison-summary.json. This identifies the fields causing the mismatch, not a proven hardware-level root cause.

Single-thread settings were already identical in both executions. No model, tokenizer, query, score precision or tie ordering was changed to make the outputs match. No claim of byte-identical output across environments is permitted. Same-machine repetition is an observation on this fixed input, not a general guarantee.

Evidence: local/result.json, github-attempt1/result.json, environment-comparison.json and github-job-attempt1.log. Reproduce with verification/check_determinism.py and a new output directory so historical outputs remain intact.
