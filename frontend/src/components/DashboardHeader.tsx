import { BUILD_LABEL } from "../buildInfo";
import type { ApiStatus, DataSource, Session } from "../types";

type Props = {
  apiStatus: ApiStatus;
  dataSource: DataSource;
  loading: boolean;
  session: Session | null;
  onRefresh: () => void;
  onSignOut: () => void;
};

export function DashboardHeader({
  apiStatus,
  dataSource,
  loading,
  session,
  onRefresh,
  onSignOut,
}: Props) {
  return (
    <header className="topbar">
      <div className="brand">
        <div className="logo" aria-hidden="true">W</div>
        <div>
          <div className="title">wilson-lab</div>
          <div className="subtitle">Secure Infrastructure Control Plane</div>
        </div>
      </div>

      <div className="header-status" aria-label="Dashboard status">
        <span className={`status-pill status-${apiStatus}`}>
          API: {apiStatus === "checking" ? "checking" : apiStatus}
        </span>
        <span className={`status-pill source-${dataSource}`}>
          {dataSource === "live" ? "Live inventory" : "Demo data"}
        </span>
        <span className="build-label mono">{BUILD_LABEL}</span>
        {session && <span className="user-pill">{session.user.username} · {session.user.role}</span>}
        <button className="btn btn-compact" type="button" onClick={onRefresh} disabled={loading}>
          Refresh
        </button>
        {session && (
          <button className="btn btn-compact" type="button" onClick={onSignOut} disabled={loading}>
            Sign out
          </button>
        )}
      </div>
    </header>
  );
}
