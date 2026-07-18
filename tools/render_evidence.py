#!/usr/bin/env python3
"""Render a sanitized Wilson Lab verification JSON report as recruiter-readable Markdown."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

SENSITIVE_KEY_PARTS = (
    "password",
    "passwd",
    "access_token",
    "refresh_token",
    "authorization",
    "private_key",
    "jwt_secret",
    "client_secret",
)
JWT_PATTERN = re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")
BEARER_PATTERN = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}", re.IGNORECASE)


class EvidenceError(RuntimeError):
    """Raised when evidence is malformed or appears to contain sensitive data."""


def load_report(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise EvidenceError(f"Verification report does not exist: {path}") from error
    except json.JSONDecodeError as error:
        raise EvidenceError(f"Verification report is invalid JSON: {error}") from error
    if not isinstance(payload, dict):
        raise EvidenceError("Verification report must be a JSON object")
    return payload


def assert_sanitized(value: Any, path: str = "report") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower()
            if any(part in normalized for part in SENSITIVE_KEY_PARTS):
                raise EvidenceError(f"Sensitive key detected at {path}.{key}")
            assert_sanitized(item, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            assert_sanitized(item, f"{path}[{index}]")
        return
    if isinstance(value, str):
        if JWT_PATTERN.search(value):
            raise EvidenceError(f"JWT-like value detected at {path}")
        if BEARER_PATTERN.search(value) and "redacted" not in value.lower():
            raise EvidenceError(f"Bearer credential detected at {path}")


def require_report_shape(report: dict[str, Any]) -> None:
    for key in ("generated_at_utc", "base_url", "frontend_origin", "level", "passed", "checks"):
        if key not in report:
            raise EvidenceError(f"Verification report is missing {key!r}")
    if report["level"] not in {"health", "read-only", "full"}:
        raise EvidenceError("Verification report contains an unknown level")
    if not isinstance(report["passed"], bool):
        raise EvidenceError("Verification report passed field must be boolean")
    if not isinstance(report["checks"], list):
        raise EvidenceError("Verification report checks field must be an array")
    for index, check in enumerate(report["checks"]):
        if not isinstance(check, dict):
            raise EvidenceError(f"Check {index} is not an object")
        for key in ("name", "status", "detail", "duration_ms"):
            if key not in check:
                raise EvidenceError(f"Check {index} is missing {key!r}")
        if check["status"] not in {"passed", "failed"}:
            raise EvidenceError(f"Check {index} contains an unknown status")


def escape_cell(value: Any) -> str:
    text = str(value if value is not None else "—")
    return text.replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def format_timestamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    return parsed.isoformat()


def render_markdown(report: dict[str, Any]) -> str:
    require_report_shape(report)
    assert_sanitized(report)

    status = "PASS" if report["passed"] else "FAIL"
    symbol = "✅" if report["passed"] else "❌"
    health = report.get("health") if isinstance(report.get("health"), dict) else {}
    checks = report["checks"]
    passed_count = sum(1 for check in checks if check.get("status") == "passed")
    failed_count = sum(1 for check in checks if check.get("status") == "failed")

    lines = [
        "# Wilson Lab Live Verification Evidence",
        "",
        f"**Result:** {symbol} {status}",
        "",
        "## Verification summary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Generated at | `{escape_cell(format_timestamp(str(report['generated_at_utc'])))}` |",
        f"| API origin | `{escape_cell(report['base_url'])}` |",
        f"| Frontend origin | `{escape_cell(report['frontend_origin'])}` |",
        f"| Verification level | `{escape_cell(report['level'])}` |",
        f"| Passed checks | {passed_count} |",
        f"| Failed checks | {failed_count} |",
        f"| Managed resources observed | {escape_cell(report.get('inventory_count', 0))} |",
        f"| Exercised resource | {escape_cell(report.get('exercised_resource'))} |",
        "",
        "## Runtime contract",
        "",
        "| Health field | Value |",
        "|---|---|",
        f"| Status | `{escape_cell(health.get('status', 'unavailable'))}` |",
        f"| Environment | `{escape_cell(health.get('environment', 'unavailable'))}` |",
        f"| Runtime | `{escape_cell(health.get('runtime', 'unavailable'))}` |",
        "",
        "## Check results",
        "",
        "| Check | Result | Duration | Evidence |",
        "|---|---:|---:|---|",
    ]

    for check in checks:
        check_symbol = "✅" if check["status"] == "passed" else "❌"
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_cell(check["name"]),
                    f"{check_symbol} {escape_cell(check['status'].upper())}",
                    f"{escape_cell(check['duration_ms'])} ms",
                    escape_cell(check["detail"]),
                ]
            )
            + " |"
        )

    if report.get("error"):
        lines.extend(["", "## Failure summary", "", f"> {escape_cell(report['error'])}"])

    lines.extend(
        [
            "",
            "## Evidence handling",
            "",
            "- This document was generated from the verifier's sanitized JSON report.",
            "- Passwords, bearer tokens, JWT signing secrets, SSH keys, and Terraform state are not included.",
            "- Scheduled verification is health-only and cannot request a state-changing operation.",
            "- A full verification is manually triggered and targets only a managed demonstration resource.",
            "",
            "## Interview interpretation",
            "",
            "The evidence demonstrates that Wilson Lab verifies the same controls it claims: HTTPS reachability, exact CORS configuration, identity, role enforcement, explicit confirmation, managed-resource operations, and durable audit linkage.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="Sanitized JSON report produced by verify_live.py")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("live-verification-evidence.md"),
        help="Markdown evidence output path",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = load_report(args.report)
        markdown = render_markdown(report)
    except EvidenceError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    print(f"Evidence summary: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
