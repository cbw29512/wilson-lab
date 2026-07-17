import { useEffect, useRef } from "react";
import type { OperationIntent } from "../types";

type Props = {
  intent: OperationIntent | null;
  loading: boolean;
  onCancel: () => void;
  onConfirm: () => void;
};

export function ConfirmDialog({ intent, loading, onCancel, onConfirm }: Props) {
  const cancelButton = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!intent) return;
    cancelButton.current?.focus();
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !loading) onCancel();
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [intent, loading, onCancel]);

  if (!intent) return null;

  return (
    <div className="overlay overlay-centered" role="presentation">
      <section className="confirm-dialog" role="alertdialog" aria-modal="true" aria-labelledby="confirm-title">
        <span className="section-kicker">Confirmation required</span>
        <h2 id="confirm-title">{intent.action} {intent.resource.name}?</h2>
        <p>
          This sends an authenticated request to the control plane. The operation and its outcome will be written to the audit log.
        </p>
        <div className="confirmation-summary">
          <span>Resource</span><strong>{intent.resource.id}</strong>
          <span>Current state</span><strong>{intent.resource.status}</strong>
          <span>Requested action</span><strong>{intent.action}</strong>
        </div>
        <div className="dialog-actions">
          <button ref={cancelButton} className="btn" type="button" onClick={onCancel} disabled={loading}>
            Cancel
          </button>
          <button className="btn btn-danger" type="button" onClick={onConfirm} disabled={loading}>
            {loading ? "Applying…" : `Confirm ${intent.action}`}
          </button>
        </div>
      </section>
    </div>
  );
}
