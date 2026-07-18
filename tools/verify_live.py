#!/usr/bin/env python3
"""Verify a deployed Wilson Lab API without exposing credentials or tokens."""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

VALID_LEVELS = ("health", "read-only", "full")
DEFAULT_FRONTEND_ORIGIN = "https://cbw29512.github.io"


class VerificationError(RuntimeError):
    """Raised when a verification assertion fails."""


class SecretToken(str):
    """String-compatible token whose value must never enter evidence output."""


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str
    duration_ms: int


@dataclass
class HttpResult:
    status: int
    headers: dict[str, str]
    payload: Any


class WilsonLabVerifier:
    def __init__(
        self,
        *,
        base_url: str,
        frontend_origin: str,
        viewer_username: str,
        viewer_password: str,
        admin_username: str,
        admin_password: str,
        level: str,
        timeout: float,
        allow_http: bool,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.frontend_origin = frontend_origin.rstrip("/")
        self.viewer_username = viewer_username
        self.viewer_password = viewer_password
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.level = level
        self.timeout = timeout
        self.allow_http = allow_http
        self.results: list[CheckResult] = []
        self.context = ssl.create_default_context()

    def verify(self) -> dict[str, Any]:
        self._check("configuration", self._verify_configuration)
        health = self._check("public health endpoint", self._verify_health)
        self._check("CORS preflight", self._verify_cors)

        inventory_count = 0
        exercised_resource: str | None = None
        if self.level in {"read-only", "full"}:
            self._check("credential configuration", self._require_credentials)
            self._check("invalid credentials rejected", self._verify_invalid_login)
            viewer_token = self._check("Viewer authentication", self._verify_viewer_login)
            viewer_inventory = self._check(
                "Viewer inventory and details",
                lambda: self._verify_viewer_inventory(viewer_token),
            )
            inventory_count = len(viewer_inventory)
            self._check(
                "Viewer authorization boundary",
                lambda: self._verify_viewer_restrictions(viewer_token, viewer_inventory),
            )

            admin_token = self._check("Administrator authentication", self._verify_admin_login)
            admin_inventory = self._check(
                "Administrator inventory",
                lambda: self._verify_admin_inventory(admin_token),
            )
            self._check(
                "explicit confirmation boundary",
                lambda: self._verify_confirmation_required(admin_token, admin_inventory),
            )
            self._check("Administrator audit access", lambda: self._verify_audit(admin_token))

            if self.level == "full":
                exercised_resource = self._check(
                    "confirmed managed operation and audit evidence",
                    lambda: self._verify_operation_and_audit(admin_token, admin_inventory),
                )

        return {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "base_url": self.base_url,
            "frontend_origin": self.frontend_origin,
            "level": self.level,
            "health": health,
            "inventory_count": inventory_count,
            "exercised_resource": exercised_resource,
            "passed": all(result.status == "passed" for result in self.results),
            "checks": [asdict(result) for result in self.results],
        }

    def _check(self, name: str, callback: Callable[[], Any]) -> Any:
        started = time.perf_counter()
        try:
            value = callback()
        except Exception as error:
            duration_ms = round((time.perf_counter() - started) * 1000)
            self.results.append(CheckResult(name, "failed", str(error), duration_ms))
            raise
        duration_ms = round((time.perf_counter() - started) * 1000)
        self.results.append(CheckResult(name, "passed", self._result_detail(value), duration_ms))
        return value

    @staticmethod
    def _result_detail(value: Any) -> str:
        if isinstance(value, SecretToken):
            return "credential accepted; bearer token redacted"
        if value is None:
            return "completed"
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return f"validated {len(value)} item(s)"
        if isinstance(value, dict):
            safe = {key: item for key, item in value.items() if key not in {"access_token", "token"}}
            return json.dumps(safe, sort_keys=True)
        return str(value)

    def _verify_configuration(self) -> str:
        parsed = urllib.parse.urlparse(self.base_url)
        if parsed.scheme not in {"https", "http"} or not parsed.netloc:
            raise VerificationError("API origin must be an absolute http(s) URL")
        if parsed.scheme != "https" and not self.allow_http:
            raise VerificationError("Live verification requires HTTPS; use --allow-http only for local tests")
        if parsed.path not in {"", "/"} or parsed.params or parsed.query or parsed.fragment:
            raise VerificationError("API origin must not contain a path, query, or fragment")
        if self.level not in VALID_LEVELS:
            raise VerificationError(f"Unknown verification level: {self.level}")
        return f"validated {parsed.scheme} origin and {self.level} level"

    def _require_credentials(self) -> str:
        missing = [
            name
            for name, value in {
                "viewer password": self.viewer_password,
                "administrator password": self.admin_password,
            }.items()
            if not value
        ]
        if missing:
            raise VerificationError(f"Missing required secret(s): {', '.join(missing)}")
        if self.viewer_password == self.admin_password:
            raise VerificationError("Viewer and Administrator passwords must differ")
        return "required credentials are present and distinct"

    def _verify_health(self) -> dict[str, str]:
        response = self._request("GET", "/health")
        self._expect_status(response, 200)
        payload = self._expect_object(response.payload, "health response")
        expected = {"status": "ok", "environment": "production", "runtime": "docker"}
        for key, value in expected.items():
            if payload.get(key) != value:
                raise VerificationError(f"Health field {key!r} was {payload.get(key)!r}, expected {value!r}")
        return {key: str(payload[key]) for key in expected}

    def _verify_cors(self) -> str:
        response = self._request(
            "OPTIONS",
            "/api/v1/inventory",
            headers={
                "Origin": self.frontend_origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization",
            },
        )
        self._expect_status(response, 200)
        allowed_origin = response.headers.get("access-control-allow-origin")
        if allowed_origin != self.frontend_origin:
            raise VerificationError(
                f"CORS allowed origin was {allowed_origin!r}, expected {self.frontend_origin!r}"
            )
        if "GET" not in response.headers.get("access-control-allow-methods", ""):
            raise VerificationError("CORS preflight did not allow GET")
        return f"allowed exact origin {allowed_origin}"

    def _verify_invalid_login(self) -> str:
        response = self._login(self.viewer_username, "definitely-not-the-real-password")
        self._expect_status(response, 401)
        return "invalid password returned 401"

    def _verify_viewer_login(self) -> SecretToken:
        token = self._expect_token(self._login(self.viewer_username, self.viewer_password))
        identity = self._identity(token)
        if identity.get("role") != "viewer" or identity.get("is_active") is not True:
            raise VerificationError("Viewer identity did not return an active viewer role")
        if identity.get("username") != self.viewer_username:
            raise VerificationError("Viewer identity username did not match the configured account")
        return token

    def _verify_admin_login(self) -> SecretToken:
        token = self._expect_token(self._login(self.admin_username, self.admin_password))
        identity = self._identity(token)
        if identity.get("role") != "admin" or identity.get("is_active") is not True:
            raise VerificationError("Administrator identity did not return an active admin role")
        if identity.get("username") != self.admin_username:
            raise VerificationError("Administrator identity username did not match the configured account")
        return token

    def _identity(self, token: str) -> dict[str, Any]:
        response = self._request("GET", "/api/v1/auth/me", token=token)
        self._expect_status(response, 200)
        return self._expect_object(response.payload, "identity response")

    def _verify_viewer_inventory(self, token: str) -> list[dict[str, Any]]:
        inventory = self._inventory(token)
        if not inventory:
            raise VerificationError("Managed inventory is empty")
        selected_id = str(inventory[0]["id"])
        response = self._request(
            "GET",
            f"/api/v1/inventory/{urllib.parse.quote(selected_id, safe='')}",
            token=token,
        )
        self._expect_status(response, 200)
        detail = self._validate_resource(response.payload)
        if detail["id"] != selected_id:
            raise VerificationError("Resource detail did not match the selected inventory item")
        return inventory

    def _verify_admin_inventory(self, token: str) -> list[dict[str, Any]]:
        inventory = self._inventory(token)
        if not inventory:
            raise VerificationError("Administrator inventory is empty")
        return inventory

    def _inventory(self, token: str) -> list[dict[str, Any]]:
        response = self._request("GET", "/api/v1/inventory", token=token)
        self._expect_status(response, 200)
        if not isinstance(response.payload, list):
            raise VerificationError("Inventory response was not a JSON array")
        resources = [self._validate_resource(item) for item in response.payload]
        identifiers = [resource["id"] for resource in resources]
        if len(identifiers) != len(set(identifiers)):
            raise VerificationError("Inventory returned duplicate resource identifiers")
        return resources

    @staticmethod
    def _validate_resource(value: Any) -> dict[str, Any]:
        resource = WilsonLabVerifier._expect_object(value, "resource")
        required_strings = ("id", "name", "type", "status", "description", "environment", "host_name")
        for field in required_strings:
            if not isinstance(resource.get(field), str) or not resource[field]:
                raise VerificationError(f"Resource field {field!r} must be a non-empty string")
        if resource["type"] not in {"container", "vm"}:
            raise VerificationError(f"Unsupported resource type: {resource['type']!r}")
        if resource["status"] not in {"running", "stopped", "planned", "error", "unknown"}:
            raise VerificationError(f"Unsupported resource status: {resource['status']!r}")
        if not isinstance(resource.get("tags"), list) or not all(
            isinstance(tag, str) for tag in resource["tags"]
        ):
            raise VerificationError("Resource tags must be an array of strings")
        if not isinstance(resource.get("allowed_actions"), list) or not all(
            action in {"start", "stop", "restart"} for action in resource["allowed_actions"]
        ):
            raise VerificationError("Resource allowed_actions contains an invalid value")
        for field in ("created_utc", "updated_utc"):
            if not isinstance(resource.get(field), str) or "T" not in resource[field]:
                raise VerificationError(f"Resource field {field!r} must be an ISO-style timestamp")
        return resource

    def _verify_viewer_restrictions(self, token: str, inventory: list[dict[str, Any]]) -> str:
        audit = self._request("GET", "/api/v1/audit?limit=1", token=token)
        self._expect_status(audit, 403)
        target = self._operation_target(inventory)
        operation = self._request(
            "POST",
            f"/api/v1/resources/{urllib.parse.quote(target['id'], safe='')}/operations",
            token=token,
            json_body={"action": target["action"], "confirmed": False},
        )
        self._expect_status(operation, 403)
        return "Viewer received 403 for audit and operation endpoints"

    def _verify_confirmation_required(self, token: str, inventory: list[dict[str, Any]]) -> str:
        target = self._operation_target(inventory)
        response = self._request(
            "POST",
            f"/api/v1/resources/{urllib.parse.quote(target['id'], safe='')}/operations",
            token=token,
            json_body={"action": target["action"], "confirmed": False},
        )
        self._expect_status(response, 409)
        payload = self._expect_object(response.payload, "confirmation response")
        if "confirmation" not in str(payload.get("detail", "")).lower():
            raise VerificationError("Unconfirmed operation did not explain the confirmation requirement")
        return f"unconfirmed {target['action']} returned 409"

    def _verify_audit(self, token: str) -> list[dict[str, Any]]:
        response = self._request("GET", "/api/v1/audit?limit=50", token=token)
        self._expect_status(response, 200)
        if not isinstance(response.payload, list):
            raise VerificationError("Audit response was not a JSON array")
        for event in response.payload:
            item = self._expect_object(event, "audit event")
            for field in ("id", "actor_id", "event_type", "outcome", "detail", "created_at"):
                if field not in item:
                    raise VerificationError(f"Audit event is missing {field!r}")
        return response.payload

    def _verify_operation_and_audit(self, token: str, inventory: list[dict[str, Any]]) -> str:
        target = self._operation_target(inventory, prefer_restart=True)
        response = self._request(
            "POST",
            f"/api/v1/resources/{urllib.parse.quote(target['id'], safe='')}/operations",
            token=token,
            json_body={"action": target["action"], "confirmed": True},
        )
        self._expect_status(response, 200)
        result = self._expect_object(response.payload, "operation result")
        request_id = result.get("request_id")
        if not isinstance(request_id, int):
            raise VerificationError("Operation result did not include an integer request_id")
        if result.get("action") != target["action"] or result.get("status") != "succeeded":
            raise VerificationError("Operation result did not report the requested successful action")
        self._validate_resource(result.get("resource"))

        matching = [
            event
            for event in self._verify_audit(token)
            if event.get("action_request_id") == request_id
        ]
        if not matching:
            raise VerificationError(f"Audit history did not contain operation request {request_id}")
        if matching[0].get("outcome") != "succeeded":
            raise VerificationError("Matching audit event did not report a succeeded outcome")
        return f"{target['action']} verified on {target['name']} ({target['id'][:12]})"

    @staticmethod
    def _operation_target(
        inventory: list[dict[str, Any]], *, prefer_restart: bool = False
    ) -> dict[str, str]:
        if prefer_restart:
            for resource in inventory:
                if "restart" in resource["allowed_actions"]:
                    return {"id": resource["id"], "name": resource["name"], "action": "restart"}
        for resource in inventory:
            if resource["allowed_actions"]:
                return {
                    "id": resource["id"],
                    "name": resource["name"],
                    "action": resource["allowed_actions"][0],
                }
        raise VerificationError("No managed resource currently exposes an allowed operation")

    def _login(self, username: str, password: str) -> HttpResult:
        body = urllib.parse.urlencode({"username": username, "password": password}).encode("utf-8")
        return self._request(
            "POST",
            "/api/v1/auth/token",
            body=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    @staticmethod
    def _expect_token(response: HttpResult) -> SecretToken:
        WilsonLabVerifier._expect_status(response, 200)
        payload = WilsonLabVerifier._expect_object(response.payload, "login response")
        token = payload.get("access_token")
        if not isinstance(token, str) or len(token) < 20:
            raise VerificationError("Login response did not include a plausible access token")
        if payload.get("token_type") != "bearer":
            raise VerificationError("Login response token_type was not bearer")
        return SecretToken(token)

    def _request(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        body: bytes | None = None,
        json_body: Any | None = None,
    ) -> HttpResult:
        request_headers = {"Accept": "application/json", "User-Agent": "wilson-lab-verifier/1.0"}
        if headers:
            request_headers.update(headers)
        if token:
            request_headers["Authorization"] = f"Bearer {token}"
        if json_body is not None:
            body = json.dumps(json_body).encode("utf-8")
            request_headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers=request_headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout, context=self.context) as response:
                return self._read_response(response.status, response.headers, response.read())
        except urllib.error.HTTPError as error:
            return self._read_response(error.code, error.headers, error.read())
        except urllib.error.URLError as error:
            raise VerificationError(f"Request to {path} failed: {error.reason}") from error

    @staticmethod
    def _read_response(status: int, headers: Any, raw: bytes) -> HttpResult:
        normalized_headers = {key.lower(): value for key, value in headers.items()}
        text = raw.decode("utf-8", errors="replace")
        if "application/json" in normalized_headers.get("content-type", "") and text:
            try:
                payload: Any = json.loads(text)
            except json.JSONDecodeError as error:
                raise VerificationError("API returned invalid JSON") from error
        else:
            payload = text
        return HttpResult(status=status, headers=normalized_headers, payload=payload)

    @staticmethod
    def _expect_status(response: HttpResult, expected: int) -> None:
        if response.status != expected:
            detail = response.payload
            if isinstance(detail, dict) and "detail" in detail:
                detail = detail["detail"]
            raise VerificationError(f"Expected HTTP {expected}, received {response.status}: {detail}")

    @staticmethod
    def _expect_object(value: Any, label: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise VerificationError(f"{label} was not a JSON object")
        return value


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=os.getenv("WILSON_LAB_API_ORIGIN", ""),
        help="API origin, or set WILSON_LAB_API_ORIGIN",
    )
    parser.add_argument(
        "--frontend-origin",
        default=os.getenv("WILSON_LAB_FRONTEND_ORIGIN", DEFAULT_FRONTEND_ORIGIN),
    )
    parser.add_argument(
        "--viewer-username",
        default=os.getenv("WILSON_LAB_VIEWER_USERNAME", "viewer"),
    )
    parser.add_argument(
        "--viewer-password",
        default=os.getenv("WILSON_LAB_VIEWER_PASSWORD", ""),
    )
    parser.add_argument(
        "--admin-username",
        default=os.getenv("WILSON_LAB_ADMIN_USERNAME", "admin"),
    )
    parser.add_argument(
        "--admin-password",
        default=os.getenv("WILSON_LAB_ADMIN_PASSWORD", ""),
    )
    parser.add_argument("--level", choices=VALID_LEVELS, default="read-only")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--allow-http", action="store_true", help="Permit HTTP for local test servers only")
    parser.add_argument("--report", type=Path, default=Path("live-verification-report.json"))
    return parser.parse_args(argv)


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.base_url:
        print("ERROR: Set --base-url or WILSON_LAB_API_ORIGIN", file=sys.stderr)
        return 2

    verifier = WilsonLabVerifier(
        base_url=args.base_url,
        frontend_origin=args.frontend_origin,
        viewer_username=args.viewer_username,
        viewer_password=args.viewer_password,
        admin_username=args.admin_username,
        admin_password=args.admin_password,
        level=args.level,
        timeout=args.timeout,
        allow_http=args.allow_http,
    )

    try:
        report = verifier.verify()
    except Exception as error:
        report = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "base_url": verifier.base_url,
            "frontend_origin": verifier.frontend_origin,
            "level": verifier.level,
            "passed": False,
            "error": str(error),
            "checks": [asdict(result) for result in verifier.results],
        }
        write_report(args.report, report)
        print(f"FAIL: {error}", file=sys.stderr)
        print(f"Sanitized report: {args.report}")
        return 1

    write_report(args.report, report)
    print(f"PASS: {len(report['checks'])} verification checks completed at level {args.level}")
    print(f"Sanitized report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
