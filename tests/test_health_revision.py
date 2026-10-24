import os
import unittest
from unittest.mock import patch

from webapp import create_app


class HealthRevisionTests(unittest.TestCase):
    def test_ready_health_exposes_render_commit(self):
        with patch.dict(os.environ, {"RENDER_GIT_COMMIT": "a" * 40}):
            response = create_app(scorer=object()).test_client().get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ready", "git_sha": "a" * 40})

    def test_unavailable_health_remains_unavailable(self):
        with patch.dict(os.environ, {}, clear=True):
            response = create_app().test_client().get("/healthz")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json, {"status": "model_unavailable", "git_sha": "unknown"})
