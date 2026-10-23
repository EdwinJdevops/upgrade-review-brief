# Third-party sources

This project includes original review code and generated lab manifests. External projects retain their own licenses and ownership.

- BAAI/bge-reranker-base: model publisher identifies MIT licensing. Model weights are downloaded separately from the hash-locked revision; they are not included in this repository. https://huggingface.co/BAAI/bge-reranker-base
- Kong Helm chart and migration guidance: https://github.com/Kong/charts . Generated lab manifests identify their upstream template paths. Documentation is fetched separately by pinned identity and is not included as a complete source snapshot.
- kube-state-metrics and its community Helm chart: https://github.com/kubernetes/kube-state-metrics and https://github.com/prometheus-community/helm-charts . Earlier controlled render and ranking experiments retain their source records.
- External Secrets migration discussion: https://github.com/external-secrets/external-secrets/issues/4662 . It is research evidence, not an executable upgrade instruction or a universal support policy.
- PyTorch, Transformers, PyYAML, Flask, Jinja, Gunicorn, Helm and the actions/checkout and actions/setup-python projects provide dependencies and tooling under their respective licenses. They are not vendored here. Playwright is used for browser verification and the actual demonstration recording; it is not a runtime dependency of the app.

The earlier negative Qwen experiments and existing-tool comparisons are retained for transparency. Source-specific findings do not establish complete migration coverage or independent competitive evaluation. AI coding assistance was used in development.
