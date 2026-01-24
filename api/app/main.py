from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="wilson-lab API", version="0.1.0")

# CORS: safe for local dev; if you later host API elsewhere, tighten this.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def run(cmd: List[str], timeout: int = 6) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError(f"cmd failed: {' '.join(cmd)}\n{p.stderr.strip()}")
    return p.stdout

def docker_inventory() -> List[Dict[str, Any]]:
    if not shutil.which("docker"):
        return []

    # One JSON object per line
    out = run(["docker", "ps", "-a", "--format", "{{json .}}"], timeout=8).splitlines()
    items: List[Dict[str, Any]] = []

    for line in out:
        try:
            d = json.loads(line)
        except Exception:
            continue

        # docker format keys usually include: Names, Image, State, Status, CreatedAt, Ports, ID
        state = (d.get("State") or "").strip().lower()
        status = "RUNNING" if state == "running" else "STOPPED"

        name = d.get("Names") or d.get("Name") or "container"
        image = d.get("Image") or ""
        created = d.get("CreatedAt") or ""
        ports = d.get("Ports") or ""

        items.append(
            {
                "id": f"docker:{name}",
                "name": name,
                "kind": "CONTAINER",
                "status": status,
                "description": f"Image: {image}" + (f" | Ports: {ports}" if ports else ""),
                "tags": ["docker"],
                "created": created,
                "updated": utc_now_iso(),
                "urls": {},
            }
        )

    return items

def virsh_inventory() -> List[Dict[str, Any]]:
    if not shutil.which("virsh"):
        return []

    names = [n.strip() for n in run(["virsh", "list", "--all", "--name"], timeout=10).splitlines() if n.strip()]
    items: List[Dict[str, Any]] = []

    for n in names:
        # domstate returns e.g. "running", "shut off"
        try:
            st = run(["virsh", "domstate", n], timeout=6).strip().lower()
        except Exception:
            st = "unknown"

        status = "RUNNING" if "running" in st else ("STOPPED" if ("shut" in st or "off" in st) else "UNKNOWN")

        items.append(
            {
                "id": f"vm:{n}",
                "name": n,
                "kind": "VM",
                "status": status,
                "description": "libvirt virtual machine",
                "tags": ["kvm", "libvirt"],
                "created": "",
                "updated": utc_now_iso(),
                "urls": {},
            }
        )

    return items

@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "time_utc": utc_now_iso()}

@app.get("/api/inventory")
def inventory() -> Dict[str, Any]:
    items = docker_inventory() + virsh_inventory()
    # Sort RUNNING first, then name
    order = {"RUNNING": 0, "STOPPED": 1, "PLANNED": 2, "UNKNOWN": 3}
    items.sort(key=lambda x: (order.get(x.get("status","UNKNOWN"), 9), x.get("name","")))
    return {"time_utc": utc_now_iso(), "items": items}
