import assert from "node:assert/strict";
import test from "node:test";
import { filterResources, formatUtc, uniqueTags } from "../src/lib/resources.ts";
import type { Resource } from "../src/types.ts";

const resources: Resource[] = [
  {
    id: "alpha",
    name: "Alpha API",
    type: "container",
    status: "running",
    description: "Primary application service",
    tags: ["api", "production-like"],
    environment: "sandbox",
    host_name: "demo-host",
    image_name: "alpha:1",
    health_status: "healthy",
    allowed_actions: ["stop", "restart"],
    created_utc: "2026-07-01T00:00:00Z",
    updated_utc: "2026-07-17T10:00:00Z",
  },
  {
    id: "beta",
    name: "Beta Database",
    type: "container",
    status: "stopped",
    description: "Training database",
    tags: ["database", "training"],
    environment: "sandbox",
    host_name: "demo-host",
    image_name: "beta:1",
    health_status: null,
    allowed_actions: ["start"],
    created_utc: "2026-07-01T00:00:00Z",
    updated_utc: "2026-07-16T10:00:00Z",
  },
];

test("collects sorted unique tags", () => {
  assert.deepEqual(uniqueTags(resources), ["all", "api", "database", "production-like", "training"]);
});

test("filters by search text and tag", () => {
  assert.deepEqual(filterResources(resources, "training", "database", "recent").map((item) => item.id), ["beta"]);
});

test("sorts resources by name", () => {
  assert.deepEqual(filterResources([...resources].reverse(), "", "all", "name").map((item) => item.id), ["alpha", "beta"]);
});

test("formats UTC values and handles invalid input", () => {
  assert.equal(formatUtc("2026-07-17T10:00:00Z"), "2026-07-17 10:00:00Z");
  assert.equal(formatUtc("not-a-date"), "Unknown");
});
