import type { Resource } from "../types";

export type ResourceSort = "recent" | "name";

export function uniqueTags(resources: Resource[]): string[] {
  return ["all", ...Array.from(new Set(resources.flatMap((resource) => resource.tags))).sort()];
}

export function filterResources(
  resources: Resource[],
  query: string,
  tag: string,
  sort: ResourceSort,
): Resource[] {
  const normalizedQuery = query.trim().toLowerCase();
  const filtered = resources.filter((resource) => {
    const searchable = [resource.name, resource.description, ...resource.tags]
      .join(" ")
      .toLowerCase();
    const matchesQuery = !normalizedQuery || searchable.includes(normalizedQuery);
    const matchesTag = tag === "all" || resource.tags.includes(tag);
    return matchesQuery && matchesTag;
  });

  return filtered.sort((left, right) => {
    if (sort === "name") return left.name.localeCompare(right.name);
    return Date.parse(right.updated_utc) - Date.parse(left.updated_utc);
  });
}

export function formatUtc(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unknown";
  return date.toISOString().replace("T", " ").replace(".000Z", "Z");
}
