from __future__ import annotations

import json
import sys
import threading
import unittest
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.verify_live import VerificationError, WilsonLabVerifier  # noqa: E402

VIEWER_TOKEN = "viewer-token-value-that-must-stay-secret"
ADMIN_TOKEN = "admin-token-value-that-must-stay-secret"
VIEWER_PASSWORD = "viewer-password-value"
ADMIN_PASSWORD = "admin-password-value"
FRONTEND_ORIGIN = "https://cbw29512.github.io"

RESOURCE = {
    "id": "demo-container-001",
    "name": "demo-web",
    "type": "container",
    "status": "running",
    "description": "Managed demonstration service.",
    "tags": ["demo", "managed"],
    "environment": "sandbox",
    "host_name": "wilson-lab-cloud",
    "image_name": "nginx:alpine",
    "health_status": "healthy",
    "allowed_actions": ["stop", "restart"],
    "created_utc": "2026-07-17T20:00:00+00:00",
    "updated_utc": "2026-07-17T20:00:00+00:00",
}


class FakeApiHandler(BaseHTTPRequestHandler):
    cors_origin = FRONTEND_ORIGIN
    audit_events: list[dict] = []
    operation_count = 0

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def _json(self, status: int, payload, headers: dict[str, str] | None = None) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _identity(self):
        authorization = self.headers.get("Authorization", "")
        if authorization == f"Bearer {VIEWER_TOKEN}":
            return {"id": 1, "username": "viewer", "role": "viewer", "is_active": True}
        if authorization == f"Bearer {ADMIN_TOKEN}":
            return {"id": 2, "username": "admin", "role": "admin", "is_active": True}
        return None

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._json(
            200,
            "OK",
            {
                "Access-Control-Allow-Origin": self.cors_origin,
                "Access-Control-Allow-Methods": "GET, POST",
                "Access-Control-Allow-Headers": "Authorization, Content-Type",
            },
        )

    def do_GET(self) -> None:  # noqa: N802
        path = urllib.parse.urlparse(self.path).path
        if path == "/health":
            self._json(200, {"status": "ok", "environment": "production", "runtime": "docker"})
            return

        identity = self._identity()
        if identity is None:
            self._json(401, {"detail": "Not authenticated"})
            return
        if path == "/api/v1/auth/me":
            self._json(200, identity)
        elif path == "/api/v1/inventory":
            self._json(200, [RESOURCE])
        elif path == f"/api/v1/inventory/{RESOURCE['id']}":
            self._json(200, RESOURCE)
        elif path == "/api/v1/audit":
            if identity["role"] != "admin":
                self._json(403, {"detail": "Administrator role required"})
            else:
                self._json(200, self.audit_events)
        else:
            self._json(404, {"detail": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urllib.parse.urlparse(self.path).path
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)

        if path == "/api/v1/auth/token":
            form = urllib.parse.parse_qs(raw.decode("utf-8"))
            username = form.get("username", [""])[0]
            password = form.get("password", [""])[0]
            if username == "viewer" and password == VIEWER_PASSWORD:
                self._json(200, {"access_token": VIEWER_TOKEN, "token_type": "bearer"})
            elif username == "admin" and password == ADMIN_PASSWORD:
                self._json(200, {"access_token": ADMIN_TOKEN, "token_type": "bearer"})
            else:
                self._json(401, {"detail": "Incorrect username or password"})
            return

        identity = self._identity()
        if identity is None:
            self._json(401, {"detail": "Not authenticated"})
            return
        if path != f"/api/v1/resources/{RESOURCE['id']}/operations":
            self._json(404, {"detail": "Not found"})
            return
        if identity["role"] != "admin":
            self._json(403, {"detail": "Administrator role required"})
            return

        operation = json.loads(raw.decode("utf-8"))
        if operation.get("confirmed") is not True:
            self._json(409, {"detail": "Explicit confirmation is required"})
            return

        type(self).operation_count += 1
        request_id = type(self).operation_count
        event = {
            "id": request_id,
            "actor_id": 2,
            "event_type": "resource.operation",
            "resource_id": RESOURCE["id"],
            "action_request_id": request_id,
            "outcome": "succeeded",
            "source_ip": "127.0.0.1",
            "detail": "restart completed for managed resource",
            "created_at": "2026-07-17T20:05:00+00:00",
        }
        type(self).audit_events.insert(0, event)
        self._json(
            200,
            {
                "request_id": request_id,
                "resource": RESOURCE,
                "action": operation.get("action"),
                "status": "succeeded",
            },
        )


class LiveVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeApiHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def setUp(self) -> None:
        FakeApiHandler.cors_origin = FRONTEND_ORIGIN
        FakeApiHandler.audit_events = []
        FakeApiHandler.operation_count = 0

    def verifier(self, level: str) -> WilsonLabVerifier:
        return WilsonLabVerifier(
            base_url=self.base_url,
            frontend_origin=FRONTEND_ORIGIN,
            viewer_username="viewer",
            viewer_password=VIEWER_PASSWORD,
            admin_username="admin",
            admin_password=ADMIN_PASSWORD,
            level=level,
            timeout=2,
            allow_http=True,
        )

    def test_health_level_requires_no_credentials(self) -> None:
        verifier = WilsonLabVerifier(
            base_url=self.base_url,
            frontend_origin=FRONTEND_ORIGIN,
            viewer_username="viewer",
            viewer_password="",
            admin_username="admin",
            admin_password="",
            level="health",
            timeout=2,
            allow_http=True,
        )
        report = verifier.verify()
        self.assertTrue(report["passed"])
        self.assertEqual(len(report["checks"]), 3)
        self.assertEqual(report["health"]["runtime"], "docker")

    def test_read_only_report_redacts_all_credentials(self) -> None:
        report = self.verifier("read-only").verify()
        evidence = json.dumps(report)
        self.assertTrue(report["passed"])
        self.assertNotIn(VIEWER_TOKEN, evidence)
        self.assertNotIn(ADMIN_TOKEN, evidence)
        self.assertNotIn(VIEWER_PASSWORD, evidence)
        self.assertNotIn(ADMIN_PASSWORD, evidence)
        self.assertIn("bearer token redacted", evidence)

    def test_full_level_records_operation_and_audit(self) -> None:
        report = self.verifier("full").verify()
        self.assertTrue(report["passed"])
        self.assertEqual(FakeApiHandler.operation_count, 1)
        self.assertEqual(report["exercised_resource"], "restart verified on demo-web (demo-contain)")
        self.assertEqual(FakeApiHandler.audit_events[0]["outcome"], "succeeded")

    def test_wrong_cors_origin_fails(self) -> None:
        FakeApiHandler.cors_origin = "https://wrong.example"
        with self.assertRaises(VerificationError):
            self.verifier("health").verify()


if __name__ == "__main__":
    unittest.main()
