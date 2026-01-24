/**
 * Purpose: wilson-lab dashboard UI (v1).
 * Why: Interview-ready SaaS-style overview of lab resources (containers/VMs) with search + tag filtering.
 * Next: Wire to backend API (/api/v1/inventory) once M2 exists; keep this mock as fallback.
 */
import { useEffect, useMemo, useState } from "react";
import "./app.css";
import { BUILD_SHA, BUILD_LABEL } from "./buildInfo";

type ResourceType = "container" | "vm";
type ResourceStatus = "running" | "stopped" | "planned" | "error" | "unknown";

type Resource = {
  id: string;
  name: string;
  type: ResourceType;
  status: ResourceStatus;
  description: string;
  tags: string[];
  created_utc: string;
  updated_utc: string;
};

function fmtUtc(iso: string): string {
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())} ${pad(
    d.getUTCHours()
  )}:${pad(d.getUTCMinutes())}:${pad(d.getUTCSeconds())}Z`;
}

function uniq<T>(arr: T[]): T[] {
  return Array.from(new Set(arr));
}

export default function App() {
  // WILSONLAB_AUTO_REFRESH_V1
  useEffect(() => {
    let stopped = false;

    const check = async () => {
      try {
        const base = (import.meta as any).env?.BASE_URL || "/";
        const url = `${base}version.json?v=${Date.now()}`;
        const r = await fetch(url, { cache: "no-store" });
        if (!r.ok) return;
        const j = await r.json();
        const live = String(j.sha || "").slice(0, 7);
        if (live && live !== BUILD_SHA) {
          // New deploy detected -> hard refresh
          if (!stopped) window.location.reload();
        }
      } catch (_e) {
        // ignore
      }
    };

    // check now + every 30s
    check();
    const id = window.setInterval(check, 30_000);
    return () => {
      stopped = true;
      window.clearInterval(id);
    };
  }, []);

  const [resources, setResources] = useState<Resource[]>([]);
  const [query, setQuery] = useState("");
  const [tag, setTag] = useState<string>("all");
  const [sort, setSort] = useState<"recent" | "name">("recent");

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}mock/resources.json`)
      .then((r) => r.json())
      .then((data) => setResources(data))
      .catch(() => setResources([]));
  }, []);

  const allTags = useMemo(() => {
    const tags = resources.flatMap((r) => r.tags || []);
    return ["all", ...uniq(tags).sort((a, b) => a.localeCompare(b))];
  }, [resources]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();

    let out = resources.filter((r) => {
      const matchesQuery =
        !q ||
        r.name.toLowerCase().includes(q) ||
        r.description.toLowerCase().includes(q) ||
        r.tags.join(" ").toLowerCase().includes(q);

      const matchesTag = tag === "all" ? true : r.tags.includes(tag);

      return matchesQuery && matchesTag;
    });

    out.sort((a, b) => {
      if (sort === "name") return a.name.localeCompare(b.name);
      return new Date(b.updated_utc).getTime() - new Date(a.updated_utc).getTime();
    });

    return out;
  }, [resources, query, tag, sort]);

  return (
    <div className="page">
      <header className="topbar">
        <div className="brand">
          <div className="logo">W</div>
          <div>
            <div className="title">wilson-lab</div>
            <div className="subtitle">Lab Orchestrator Dashboard</div>
          </div>
        </div>

        <div className="controls">
          <input
            className="search"
            placeholder="Search resources, tags, descriptions…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />

          <select className="select" value={tag} onChange={(e) => setTag(e.target.value)}>
            {allTags.map((t) => (
              <option key={t} value={t}>
                {t === "all" ? "All tags" : t}
              </option>
            ))}
          </select>

          <select className="select" value={sort} onChange={(e) => setSort(e.target.value as any)}>
            <option value="recent">Sort: Most recent</option>
            <option value="name">Sort: Name</option>
          </select>
        </div>
      </header>

      <main className="content">
        <div className="meta">
          <div className="meta-left">
            <span className="pill">UTC</span>
            <span className="muted">{filtered.length} resources</span>
          </div>
          <div className="meta-right muted">v1 mock inventory (M1) → real API inventory (M2) <span className="mono"> • {BUILD_LABEL}</span></div>
        </div>

        <div className="grid">
          {filtered.map((r) => (
            <article key={r.id} className="card">
              <div className="card-top">
                <div>
                  <div className="card-title">{r.name}</div>
                  <div className="card-subtitle">
                    <span className={`badge badge-${r.type}`}>{r.type.toUpperCase()}</span>
                    <span className={`badge badge-status badge-${r.status}`}>{r.status}</span>
                  </div>
                </div>
              </div>

              <p className="desc">{r.description}</p>

              <div className="tags">
                {r.tags.map((t) => (
                  <span key={t} className="tag">
                    {t}
                  </span>
                ))}
              </div>

              <div className="times">
                <div className="time-row">
                  <span className="muted">Created</span>
                  <span className="mono">{fmtUtc(r.created_utc)}</span>
                </div>
                <div className="time-row">
                  <span className="muted">Updated</span>
                  <span className="mono">{fmtUtc(r.updated_utc)}</span>
                </div>
              </div>

              <div className="actions">
                <button className="btn" disabled>View</button>
                <button className="btn btn-primary" disabled>Actions</button>
              </div>
            </article>
          ))}
        </div>

        {resources.length === 0 && (
          <div className="empty">
            <div className="empty-title">No resources loaded</div>
            <div className="muted">
              Expected <span className="mono">public/mock/resources.json</span>.
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
