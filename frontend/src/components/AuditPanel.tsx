import { formatUtc } from "../lib/resources";
import type { AuditEvent } from "../types";

type Props = {
  events: AuditEvent[];
  open: boolean;
  onClose: () => void;
};

export function AuditPanel({ events, open, onClose }: Props) {
  if (!open) return null;

  return (
    <div className="overlay" role="presentation" onMouseDown={onClose}>
      <aside
        className="drawer audit-drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="audit-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="panel-heading">
          <div>
            <span className="section-kicker">Administrator evidence</span>
            <h2 id="audit-title">Audit timeline</h2>
          </div>
          <button className="icon-button" type="button" onClick={onClose} aria-label="Close audit timeline">×</button>
        </div>

        {events.length === 0 ? (
          <div className="empty compact-empty">
            <strong>No audit events yet</strong>
            <p>Successful and failed resource operations will appear here.</p>
          </div>
        ) : (
          <ol className="audit-list">
            {events.map((event) => (
              <li key={event.id} className={`audit-event audit-${event.outcome}`}>
                <div className="audit-event-heading">
                  <strong>{event.event_type}</strong>
                  <span className="badge">{event.outcome}</span>
                </div>
                <p>{event.detail}</p>
                <dl>
                  <div><dt>Resource</dt><dd className="mono">{event.resource_id || "n/a"}</dd></div>
                  <div><dt>Request</dt><dd>{event.action_request_id || "n/a"}</dd></div>
                  <div><dt>Actor</dt><dd>{event.actor_id}</dd></div>
                  <div><dt>Time</dt><dd className="mono">{formatUtc(event.created_at)}</dd></div>
                </dl>
              </li>
            ))}
          </ol>
        )}
      </aside>
    </div>
  );
}
