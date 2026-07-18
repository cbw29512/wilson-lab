from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.render_evidence import EvidenceError, assert_sanitized, render_markdown  # noqa: E402


class EvidenceRendererTests(unittest.TestCase):
    def report(self, *, passed: bool = True) -> dict:
        return {
            "generated_at_utc": "2026-07-18T02:00:00+00:00",
            "base_url": "https://api.example.com",
            "frontend_origin": "https://cbw29512.github.io",
            "level": "full",
            "health": {"status": "ok", "environment": "production", "runtime": "docker"},
            "inventory_count": 2,
            "exercised_resource": "restart verified on demo-web (abc123)",
            "passed": passed,
            "checks": [
                {
                    "name": "public health endpoint",
                    "status": "passed",
                    "detail": '{"environment": "production", "runtime": "docker", "status": "ok"}',
                    "duration_ms": 25,
                },
                {
                    "name": "Viewer authentication",
                    "status": "passed",
                    "detail": "credential accepted; bearer token redacted",
                    "duration_ms": 30,
                },
            ],
        }

    def test_rendered_markdown_contains_core_evidence(self) -> None:
        markdown = render_markdown(self.report())
        self.assertIn("✅ PASS", markdown)
        self.assertIn("Managed resources observed | 2", markdown)
        self.assertIn("Viewer authentication", markdown)
        self.assertIn("bearer token redacted", markdown)
        self.assertIn("production", markdown)

    def test_failed_report_is_rendered_without_hiding_failure(self) -> None:
        report = self.report(passed=False)
        report["error"] = "Expected HTTP 200, received 503"
        report["checks"].append(
            {
                "name": "Administrator audit access",
                "status": "failed",
                "detail": "Expected HTTP 200, received 503",
                "duration_ms": 10,
            }
        )
        markdown = render_markdown(report)
        self.assertIn("❌ FAIL", markdown)
        self.assertIn("Failure summary", markdown)
        self.assertIn("received 503", markdown)

    def test_sensitive_key_is_rejected(self) -> None:
        report = self.report()
        report["access_token"] = "must-not-appear"
        with self.assertRaises(EvidenceError):
            assert_sanitized(report)

    def test_jwt_like_value_is_rejected(self) -> None:
        report = self.report()
        report["checks"][0]["detail"] = "eyJheader.payload.signature"
        with self.assertRaises(EvidenceError):
            render_markdown(report)

    def test_bearer_value_is_rejected_unless_redacted(self) -> None:
        report = self.report()
        report["checks"][0]["detail"] = "Bearer abcdefghijklmnopqrstuvwxyz"
        with self.assertRaises(EvidenceError):
            render_markdown(report)

    def test_rendered_document_does_not_add_sensitive_fields(self) -> None:
        markdown = render_markdown(self.report())
        serialized = json.dumps(self.report())
        self.assertNotIn("access_token", markdown)
        self.assertNotIn("private_key", markdown)
        self.assertNotIn("jwt_secret", markdown)
        self.assertIn("bearer token redacted", serialized)


if __name__ == "__main__":
    unittest.main()
