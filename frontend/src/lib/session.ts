import type { Session, User } from "../types";

const SESSION_KEY = "wilson-lab-session-v1";

type StorageLike = Pick<Storage, "getItem" | "setItem" | "removeItem">;

function isUser(value: unknown): value is User {
  if (!value || typeof value !== "object") return false;
  const user = value as Record<string, unknown>;
  return (
    typeof user.id === "number" &&
    typeof user.username === "string" &&
    (user.role === "viewer" || user.role === "admin") &&
    typeof user.is_active === "boolean"
  );
}

function browserStorage(): StorageLike | undefined {
  try {
    return typeof window === "undefined" ? undefined : window.sessionStorage;
  } catch {
    return undefined;
  }
}

export function readSession(storage: StorageLike | undefined = browserStorage()): Session | null {
  if (!storage) return null;
  try {
    const raw = storage.getItem(SESSION_KEY);
    if (!raw) return null;
    const value = JSON.parse(raw) as Record<string, unknown>;
    if (typeof value.token !== "string" || !isUser(value.user)) return null;
    return { token: value.token, user: value.user };
  } catch {
    return null;
  }
}

export function saveSession(session: Session, storage: StorageLike | undefined = browserStorage()): void {
  try {
    storage?.setItem(SESSION_KEY, JSON.stringify(session));
  } catch {
    // The active session still works in memory when browser storage is unavailable.
  }
}

export function clearSession(storage: StorageLike | undefined = browserStorage()): void {
  try {
    storage?.removeItem(SESSION_KEY);
  } catch {
    // Nothing else is required when storage access is unavailable.
  }
}
