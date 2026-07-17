import { useMemo, useState } from "react";
import "./app.css";
import { AuditPanel } from "./components/AuditPanel";
import { ConfirmDialog } from "./components/ConfirmDialog";
import { DashboardControls } from "./components/DashboardControls";
import { DashboardHeader } from "./components/DashboardHeader";
import { LoginPanel } from "./components/LoginPanel";
import { NoticeBanner } from "./components/NoticeBanner";
import { ResourceCard } from "./components/ResourceCard";
import { ResourceDrawer } from "./components/ResourceDrawer";
import { useDeploymentRefresh } from "./hooks/useDeploymentRefresh";
import { useLabDashboard } from "./hooks/useLabDashboard";
import { filterResources, uniqueTags, type ResourceSort } from "./lib/resources";
import type { OperationIntent, Resource } from "./types";

export default function App() {
  useDeploymentRefresh();
  const dashboard = useLabDashboard();
  const [query, setQuery] = useState("");
  const [tag, setTag] = useState("all");
  const [sort, setSort] = useState<ResourceSort>("recent");
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null);
  const [pendingOperation, setPendingOperation] = useState<OperationIntent | null>(null);
  const [auditOpen, setAuditOpen] = useState(false);

  const tags = useMemo(() => uniqueTags(dashboard.resources), [dashboard.resources]);
  const filtered = useMemo(
    () => filterResources(dashboard.resources, query, tag, sort),
    [dashboard.resources, query, sort, tag],
  );

  async function confirmOperation() {
    if (!pendingOperation) return;
    const updated = await dashboard.operate(pendingOperation);
    if (updated && selectedResource?.id === updated.id) setSelectedResource(updated);
    setPendingOperation(null);
  }

  async function signOut() {
    setSelectedResource(null);
    setAuditOpen(false);
    await dashboard.signOut();
  }

  return (
    <div className="page">
      <DashboardHeader
        apiStatus={dashboard.apiStatus}
        dataSource={dashboard.dataSource}
        loading={dashboard.loading}
        session={dashboard.session}
        onRefresh={() => void dashboard.refresh()}
        onSignOut={() => void signOut()}
      />

      <main className="content">
        <NoticeBanner notice={dashboard.notice} />
        {!dashboard.session && (
          <LoginPanel
            apiStatus={dashboard.apiStatus}
            loading={dashboard.loading}
            onSignIn={dashboard.signIn}
          />
        )}

        <section className="dashboard-toolbar" aria-label="Inventory controls">
          <div className="inventory-summary">
            <span className="pill">UTC</span>
            <strong>{filtered.length}</strong>
            <span className="muted">of {dashboard.resources.length} resources</span>
            {dashboard.loading && <span className="loading-label">Refreshing…</span>}
          </div>
          <DashboardControls
            query={query}
            tag={tag}
            sort={sort}
            tags={tags}
            onQueryChange={setQuery}
            onTagChange={setTag}
            onSortChange={setSort}
          />
          {dashboard.session?.user.role === "admin" && (
            <button className="btn audit-button" type="button" onClick={() => setAuditOpen(true)}>
              Audit timeline <span className="count-badge">{dashboard.auditEvents.length}</span>
            </button>
          )}
        </section>

        <section className="grid" aria-label="Lab resources">
          {filtered.map((resource) => (
            <ResourceCard
              key={resource.id}
              resource={resource}
              session={dashboard.session}
              loading={dashboard.loading}
              onView={setSelectedResource}
              onOperate={setPendingOperation}
            />
          ))}
        </section>

        {!dashboard.loading && filtered.length === 0 && (
          <div className="empty">
            <strong>No matching resources</strong>
            <p>Clear the search or choose a different tag.</p>
          </div>
        )}
      </main>

      <ResourceDrawer
        resource={selectedResource}
        session={dashboard.session}
        loading={dashboard.loading}
        onClose={() => setSelectedResource(null)}
        onOperate={setPendingOperation}
      />
      <ConfirmDialog
        intent={pendingOperation}
        loading={dashboard.loading}
        onCancel={() => setPendingOperation(null)}
        onConfirm={() => void confirmOperation()}
      />
      <AuditPanel events={dashboard.auditEvents} open={auditOpen} onClose={() => setAuditOpen(false)} />
    </div>
  );
}
