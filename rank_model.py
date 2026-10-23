"""Purpose-trained local text relevance model. Scores do not prove applicability."""
import math
import os
import time
from pathlib import Path

from download_reranker import MODEL, REVISION, FILES, identity


class LocalReranker:
    def __init__(self, model_dir: Path):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        for name, (size, kind, digest) in FILES.items():
            if identity(model_dir / name, size, kind) != digest:
                raise ValueError("Reranker file is missing or differs from the pinned revision: " + name)
        self.torch = torch
        threads = int(os.environ.get("RERANKER_CPU_THREADS", "4"))
        if not 1 <= threads <= 4:
            raise ValueError("RERANKER_CPU_THREADS must be between 1 and 4")
        torch.set_num_threads(threads)
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True, trust_remote_code=False)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_dir, local_files_only=True, trust_remote_code=False,
            use_safetensors=True, torch_dtype=torch.float32,
        ).eval()

    def score(self, query: str, passage: str, window_limit: int = 32) -> dict:
        if window_limit <= 0:
            return {"score": None, "model_executed": False, "window_count": 0,
                    "reason": "request_window_budget_exhausted"}
        if len(query) > 10000 or len(passage) > 10000:
            raise ValueError("Reranker input exceeds character limit")
        query_tokens = len(self.tokenizer.encode(query, add_special_tokens=False))
        if query_tokens > 384:
            return {"score": None, "model_executed": False, "input_tokens": query_tokens, "window_count": 0, "reason": "query_too_long_no_silent_truncation"}
        # Overflow windows cover the complete passage rather than discarding its tail.
        inputs = self.tokenizer(query, passage, return_tensors="pt", padding=True,
                                truncation="only_second", max_length=512, stride=32,
                                return_overflowing_tokens=True)
        inputs.pop("overflow_to_sample_mapping", None)
        windows = int(inputs["input_ids"].shape[0])
        if windows > min(32, window_limit):
            return {"score": None, "model_executed": False, "window_count": 0, "reason": "too_many_windows_not_partially_scored"}
        started = time.perf_counter()
        values = []
        with self.torch.inference_mode():
            for i in range(windows):
                window = {key: value[i:i+1] for key,value in inputs.items()}
                logits = self.model(**window, return_dict=True).logits.view(-1).float()
                if logits.numel() != 1 or not math.isfinite(float(logits[0])):
                    raise ValueError("Expected one finite relevance score per window")
                values.append(float(logits[0]))
        return {"score": round(max(values), 6), "model_executed": True,
                "window_count": windows, "window_scores": [round(x, 6) for x in values],
                "input_tokens_including_overlap": int(inputs["attention_mask"].sum()),
                "inference_seconds": round(time.perf_counter() - started, 4),
                "reason": "relative_relevance_only_not_confidence_or_upgrade_approval"}
