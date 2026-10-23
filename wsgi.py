"""Load one verified CPU model before accepting review requests."""
import os
from pathlib import Path

from rank_model import LocalReranker
from webapp import ROOT, create_app

app = create_app(LocalReranker(Path(os.environ.get("MODEL_DIR", str(ROOT / ".models/bge-reranker-base")))))
