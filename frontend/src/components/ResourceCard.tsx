import { formatUtc } from "../lib/resources";
import type { OperationIntent, Resource, Session } from "../types";

type Props = {
  resource: Resource;
  session: Session | null;
  loading: boolean;
  onView: (resource: Resource) => void;
  onOperate: (intent: OperationIntent) => void;
};

export function ResourceCard({ resource, session, loading, onView, onOperate }: Props) {
  const isAdmin = session?.user.role === "admin";

  return (
    <article className="card">
      <div className="card-top">
        <div>
          <h2 className="card-title">{resource.name}</h2>
          <div className="card-subtitle">
            <span className={`badge badge-${resource.type}`}>{resource.type.toUpperCase()}</span>
            <span className={`badge badge-status badge-${resource.status}`}>{resource.status}</span>
            {resource.health_status && <span className="badge">health: {resource.health_status}</span>}
          </div>
        </div>
      </div>

      <p className="desc">{resource.description}</p>
      <div className="tags">
        {resource.tags.map((tag) => <span key={tag} className="tag">{tag}</span>)}
      </div>

      <dl className="resource-facts">
        <div><dt>Environment</dt><dd>{resource.environment}</dd></div>
        <div><dt>Host</dt><dd>{resource.host_name}</dd></div>
        <div><dt>Updated</dt><dd className="mono">{formatUtc(resource.updated_utc)}</dd></div>
      </dl>

      <div className="actions">
        <button className="btn" type="button" onClick={() => onView(resource)}>View details</button>
        {isAdmin && resource.allowed_actions.map((action) => (
          <button
            key={action}
            className="btn btn-primary"
            type="button"
            disabled={loading}
            onClick={() => onOperate({ resource, action })}
          >
            {action}
          </button>
        ))}
        {!isAdmin && session && <span className="role-note">Viewer access: read only</span>}
      </div>
    </article>
  );
}
