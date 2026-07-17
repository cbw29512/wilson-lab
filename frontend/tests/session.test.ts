import assert from "node:assert/strict";
import test from "node:test";
import { clearSession, readSession, saveSession } from "../src/lib/session.ts";
import type { Session } from "../src/types.ts";

class MemoryStorage {
  private values = new Map<string, string>();
  getItem(key: string) { return this.values.get(key) ?? null; }
  setItem(key: string, value: string) { this.values.set(key, value); }
  removeItem(key: string) { this.values.delete(key); }
}

const session: Session = {
  token: "signed-token",
  user: { id: 1, username: "viewer", role: "viewer", is_active: true },
};

test("saves and restores a valid session", () => {
  const storage = new MemoryStorage();
  saveSession(session, storage);
  assert.deepEqual(readSession(storage), session);
});

test("rejects malformed stored session data", () => {
  const storage = new MemoryStorage();
  storage.setItem("wilson-lab-session-v1", JSON.stringify({ token: 42, user: {} }));
  assert.equal(readSession(storage), null);
});

test("clears stored session data", () => {
  const storage = new MemoryStorage();
  saveSession(session, storage);
  clearSession(storage);
  assert.equal(readSession(storage), null);
});
