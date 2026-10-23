# Local extraction baseline

Executed October 20, 2026, on the assistant's Linux CPU runtime. No installation was made on Edwin's laptop. No provider model API, fine-tuning, or paid deployment was used.

## Result

Six single-run prompts were evaluated with Qwen/Qwen3-0.6B at revision `c1899de289a04d12100db370d81485cdf75e47ca`. The downloaded weight matched its published LFS SHA-256. The run used Transformers 4.57.1, CPU PyTorch 2.14.1, float32, four intra-op threads, fixed seed and non-thinking mode.

- Four focused extraction tasks from public project documentation and two synthetic checks (insufficient information and an appended adversarial instruction).
- Six outputs parsed as JSON.
- Five failed the predeclared citation contract; one passed, the insufficient-information abstention.
- Author inspection also found omitted important conditions and incomplete actions. These are separate from quote formatting failures.
- The adversarial case did not emit the requested deployment approval, but its extraction remained deficient. A single such observation cannot establish prompt-injection robustness.
- Total generation time was 74.892 seconds, excluding loading and preparation. Peak process RSS was 4750.1 MiB. This is not a production latency or memory guarantee.

This is a small feasibility smoke test with author-defined tasks. Cases share source documents, were not independently labeled, and are not a representative or held-out benchmark. Public text may be in pretraining. A 1/6 contract-valid count is not an accuracy estimate for this model family, larger models, or production use. No stronger-model comparison has run.

## Files and evidence

`frozen-contract.json` records the prompt, source excerpt hashes, expected review obligations and generation settings saved before generation. `published-results.json` records metrics and SHA-256 of each exact original response. Long source quotations and exact raw responses are omitted from the deliverable; the run script regenerates them locally. No model output became an approved rule or executed code.

`model-download-lock.json` resolves the model revision and upstream file metadata; `download-result.json` records downloaded bytes/hashes. `environment-freeze.txt` records the actual isolated Python environment. Model weights, the virtual environment, raw source documents and caches are excluded from the deliverable.

## Optional reproduction

The weight download is approximately 1.5 GB and the observed process used about 4.6 GiB of memory, before accounting for Windows/WSL and other applications. Reproduction is optional; normal artifact checks do not require this model.

Create an isolated Python 3.12 environment. Install `torch==2.14.1+cpu` from `https://download.pytorch.org/whl/cpu`, then the remaining exact versions from `environment-freeze.txt` using PyPI. Run the following from this directory:

```bash
python download_model.py
python prepare_sources.py
python run_local_baseline.py --model-dir weights --source-dir sources
```

The source preparer verifies Git blob identities and refuses a changed ESO issue body. The run refuses to overwrite a changed frozen contract. Do not tune the prompt against these cases and then report them as untouched evaluation data. Bitwise output reproducibility across different hardware/software backends is not guaranteed.

Official model card: https://huggingface.co/Qwen/Qwen3-0.6B

The local baseline does not select our production model. Qwen3-8B and hosted routes remain untested. Tinker training has no demonstrated justification yet.
