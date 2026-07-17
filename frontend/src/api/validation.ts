import type { AuditEvent, Resource, User } from "../types";

function record(value: unknown): Record<string, unknown> | null {
  return value && typeof value === "object" ? (value as Record<string, unknown>) : null;
}

function nullableString(value: unknown): boolean {
  return value === null || typeof value === "string";
}

export function parseUser(value: unknown): User {
  const item = record(value);
  if (
    !item ||
    typeof item.id !== "number" ||
    typeof item.username !== "string" ||
    (item.role !== "viewer" && item.role !== "admin") ||
    typeof item.is_active !== "boolean"
  ) {
    throw new Error("The API returned an invalid user response");
  }
  return item as unknown as User;
}

export function parseResource(value: unknown): Resource {
  const item = record(value);
  const actions = item?.allowed_actions;
  const tags = item?.tags;
  if (
    !item ||
    typeof item.id !== "string" ||
    typeof item.name !== "string" ||
    (item.type !== "container" && item.type !== "vm") ||
    !["running", "stopped", "planned", "error", "unknown"].includes(String(item.status)) ||
    typeof item.description !== "string" ||
    !Array.isArray(tags) ||
    !tags.every((tag) => typeof tag === "string") ||
    !Array.isArray(actions) ||
    !actions.every((action) => ["start", "stop", "restart"].includes(String(action))) ||
    typeof item.environment !== "string" ||
    typeof item.host_name !== "string" ||
    !nullableString(item.image_name) ||
    !nullableString(item.health_status) ||
    typeof item.created_utc !== "string" ||
    typeof item.updated_utc !== "string"
  ) {
    throw new Error("The API returned an invalid resource response");
  }
  return item as unknown as Resource;
}

export function parseResources(value: unknown): Resource[] {
  if (!Array.isArray(value)) throw new Error("The API returned an invalid inventory response");
  return value.map(parseResource);
}

export function parseAuditEvents(value: unknown): AuditEvent[] {
  if (!Array.isArray(value)) throw new Error("The API returned an invalid audit response");
  return value.map((entry) => {
    const item = record(entry);
    if (
      !item ||
      typeof item.id !== "number" ||
      typeof item.actor_id !== "number" ||
      typeof item.event_type !== "string" ||
      !nullableString(item.resource_id) ||
      !(item.action_request_id === null || typeof item.action_request_id === "number") ||
      typeof item.outcome !== "string" ||
      !nullableString(item.source_ip) ||
      typeof item.detail !== "string" ||
      typeof item.created_at !== "string"
    ) {
      throw new Error("The API returned an invalid audit event");
    }
    return item as unknown as AuditEvent;
  });
}
