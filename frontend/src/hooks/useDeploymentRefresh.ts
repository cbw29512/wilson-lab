import { useEffect } from "react";
import { BUILD_SHA } from "../buildInfo";

export function useDeploymentRefresh(): void {
  useEffect(() => {
    let stopped = false;
    const check = async () => {
      try {
        const response = await fetch(`${import.meta.env.BASE_URL}version.json?v=${Date.now()}`, {
          cache: "no-store",
        });
        if (!response.ok) return;
        const payload = (await response.json()) as { sha?: unknown };
        const liveSha = String(payload.sha || "").slice(0, 7);
        if (liveSha && liveSha !== BUILD_SHA && !stopped) window.location.reload();
      } catch {
        // Deployment polling is best-effort and should never interrupt the dashboard.
      }
    };

    void check();
    const interval = window.setInterval(check, 30_000);
    return () => {
      stopped = true;
      window.clearInterval(interval);
    };
  }, []);
}
