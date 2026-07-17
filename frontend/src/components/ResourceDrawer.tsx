import { useEffect } from "react";
import { formatUtc } from "../lib/resources";
import type { OperationIntent, Resource, Session } from "../types";

type Props = {
  resource: Resource | null;
  session: Session | null;
  loading: boolean;
  onClose: () => void;
  onOperate: (intent: OperationIntent) => void;
};

export function ResourceDrawer({ resource, session, loading, onClose, onOperate }: Props) {
  useEffect(() => {
    if (!resource) return;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [onClose, resource]);

  if (!resource) return null;
  const isAdmin = session?.user.role === "admin";

  return (
    <div className="overlay" role="presentation" onMouseDown={onClose}>
      <aside
        className="drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="resource-detail-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="panel-heading">
          <div>
            <span className="section-kicker">Resource detail</span>
            <h2 id="resource-detail-title">{resource.name}</h2>
          </div>
          <button className="icon-button" type="button" onClick={onClose} aria-label="Close resource details">×</button>
        </div>

        <p>{resource.description}</p>
        <dl className="detail-list">
          <div><dt>ID</dt><dd className="mono">{resource.id}</dd></div>
          <div><dt>Type</dt><dd>{resource.type}</dd></div>
          <div><dt>Status</dt><dd>{resource.status}</dd></div>
          <div><dt>Environment</dt><dd>{resource.environment}</dd></div>
          <div><dt>Host</dt><dd>{resource.host_name}</dd></div>
          <div><dt>Image</dt><dd className="mono">{resource.image_name || "Not reported"}</dd></div>
          <div><dt>Health</dt><dd>{resource.health_status || "Not reported"}</dd></div>
          <div><dt>Created</dt><dd className="mono">{formatUtc(resource.created_utc)}</dd></div>
          <div><dt>Updated</dt><dd className="mono">{formatUtc(resource.updated_utc)}</dd></div>
        </dl>

        <div className="tags">
          {resource.tags.map((tag) => <span key={tag} className="tag">{tag}</span>)}
        </div>

        <div className="panel-actions">
          {isAdmin && resource.allowed_actions.map((action) => (
            <button
              key={action}
              className="btn btn-primary"
              type="button"
              disabled={loading}
              onClick={() => onOperate({ resource, action })}
            >
              {action} resource
            </button>
          ))}
          {!isAdmin && <p className="role-note">Administrator access is required for resource operations.</p>}
        </div>
      </aside>
    </div>
  );
}
