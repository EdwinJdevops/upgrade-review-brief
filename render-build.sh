#!/usr/bin/env bash
set -euo pipefail
python -m pip install --disable-pip-version-check --no-cache-dir -r requirements-web.txt
python -m pip install --disable-pip-version-check --no-cache-dir torch==2.14.1+cpu --index-url https://download.pytorch.org/whl/cpu
python -m pip install --disable-pip-version-check --no-cache-dir transformers==4.57.1
python prepare_brief_source.py
python download_reranker.py .models/bge-reranker-base
