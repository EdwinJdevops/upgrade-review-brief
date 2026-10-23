# Recorded demonstration

`browser-demo.mp4` records a genuine local browser session against Gunicorn and the verified BAAI BGE CPU model. It shows the home page, an actual model review of the controlled Kong example, the selected readiness-path diff, retained passage locations, unresolved context and both report downloads. No simulated model response or live Render deployment is shown. The original capture was compressed to a 960-pixel-wide MP4; it was not replaced with generated frames.

The mobile uploads and checks are recorded separately in `verification/web-browser-2026-10-23.json`, alongside the actual desktop report. PNG screenshots are direct browser captures. No general accessibility or cross-browser certification is claimed.

To reproduce the captures on Linux with Python 3.12, installed application/model dependencies and FFmpeg, install `playwright==1.56.0`, run `python -m playwright install chromium`, then run `python verification/capture_browser.py` from the repository root. The recording tool starts and stops its own local server. It is verification tooling, not a runtime dependency of the deployed application.
