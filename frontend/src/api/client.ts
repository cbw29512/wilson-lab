import type { AuditEvent, OperationResult, Resource, ResourceAction, User } from "../types";
import { parseAuditEvents, parseResource, parseResources, parseUser } from "./validation";

const API_ORIGIN = (import.meta.env.VITE_API_ORIGIN || "").trim().replace(/\/$/, "");

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

function url(path: string): string {
  return `${API_ORIGIN}${path}`;
}

async function readPayload(response: Response): Promise<unknown> {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return response.json();
  return response.text();
}

async function request(path: string, init: RequestInit = {}, token?: string): Promise<unknown> {
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(url(path), { ...init, headers, cache: "no-store" });
  const payload = await readPayload(response);
  if (!response.ok) {
    const detail =
      payload && typeof payload === "object" && "detail" in payload
        ? String((payload as { detail: unknown }).detail)
        : String(payload || `Request failed with status ${response.status}`);
    throw new ApiError(detail, response.status);
  }
  return payload;
}

export async function checkApi(): Promise<boolean> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 2500);
  try {
    const response = await fetch(url("/health"), {
      cache: "no-store",
      signal: controller.signal,
    });
    return response.ok;
  } catch {
    return false;
  } finally {
    window.clearTimeout(timeout);
  }
}

export async function login(username: string, password: string): Promise<string> {
  const body = new URLSearchParams({ username, password });
  const payload = await request("/api/v1/auth/token", {
    method: "POST",
    body,
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  if (!payload || typeof payload !== "object" || typeof (payload as { access_token?: unknown }).access_token !== "string") {
    throw new Error("The API returned an invalid login response");
  }
  return (payload as { access_token: string }).access_token;
}

export async function getCurrentUser(token: string): Promise<User> {
  return parseUser(await request("/api/v1/auth/me", {}, token));
}

export async function getInventory(token: string): Promise<Resource[]> {
  return parseResources(await request("/api/v1/inventory", {}, token));
}

export async function getResource(token: string, resourceId: string): Promise<Resource> {
  return parseResource(await request(`/api/v1/inventory/${encodeURIComponent(resourceId)}`, {}, token));
}

export async function operateResource(
  token: string,
  resourceId: string,
  action: ResourceAction,
): Promise<OperationResult> {
  const payload = await request(
    `/api/v1/resources/${encodeURIComponent(resourceId)}/operations`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, confirmed: true }),
    },
    token,
  );
  if (!payload || typeof payload !== "object") throw new Error("The API returned an invalid operation response");
  const result = payload as Record<string, unknown>;
  return {
    request_id: Number(result.request_id),
    resource: parseResource(result.resource),
    action: String(result.action) as ResourceAction,
    status: String(result.status),
  };
}

export async function getAudit(token: string): Promise<AuditEvent[]> {
  return parseAuditEvents(await request("/api/v1/audit?limit=50", {}, token));
}
