import { useState, type FormEvent } from "react";
import type { ApiStatus } from "../types";

type Props = {
  apiStatus: ApiStatus;
  loading: boolean;
  onSignIn: (username: string, password: string) => Promise<void>;
};

export function LoginPanel({ apiStatus, loading, onSignIn }: Props) {
  const [username, setUsername] = useState("viewer");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const available = apiStatus === "available";

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      await onSignIn(username.trim(), password);
      setPassword("");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Sign-in failed");
    }
  }

  return (
    <section className="login-panel" aria-labelledby="login-title">
      <div>
        <span className="section-kicker">Authenticated demonstration</span>
        <h1 id="login-title">Connect to the Wilson Lab sandbox</h1>
        <p>
          Public visitors can explore safe demo data. Authorized Viewer and Admin accounts can switch this dashboard to live inventory.
        </p>
      </div>

      <form className="login-form" onSubmit={submit}>
        <label>
          Username
          <input
            autoComplete="username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            disabled={!available || loading}
          />
        </label>
        <label>
          Password
          <input
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            disabled={!available || loading}
          />
        </label>
        <button className="btn btn-primary" type="submit" disabled={!available || loading || !username.trim() || !password}>
          {loading ? "Connecting…" : "Sign in"}
        </button>
        {apiStatus === "checking" && <p className="form-help">Checking API availability…</p>}
        {apiStatus === "unavailable" && (
          <p className="form-help">The cloud API is not connected yet. Demo mode remains fully available.</p>
        )}
        {error && <p className="form-error" role="alert">{error}</p>}
      </form>
    </section>
  );
}
