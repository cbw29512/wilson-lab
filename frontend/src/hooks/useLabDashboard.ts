import { useCallback, useEffect, useState } from "react";
import {
  ApiError,
  checkApi,
  getAudit,
  getCurrentUser,
  getInventory,
  login,
  operateResource,
} from "../api/client";
import { parseResources } from "../api/validation";
import { clearSession, readSession, saveSession } from "../lib/session";
import type {
  ApiStatus,
  AuditEvent,
  DataSource,
  Notice,
  OperationIntent,
  Resource,
  Session,
} from "../types";

export function useLabDashboard() {
  const [apiStatus, setApiStatus] = useState<ApiStatus>("checking");
  const [dataSource, setDataSource] = useState<DataSource>("demo");
  const [session, setSession] = useState<Session | null>(() => readSession());
  const [resources, setResources] = useState<Resource[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [notice, setNotice] = useState<Notice | null>(null);

  const loadDemo = useCallback(async () => {
    const response = await fetch(`${import.meta.env.BASE_URL}mock/resources.json`, { cache: "no-store" });
    if (!response.ok) throw new Error("Demo inventory could not be loaded");
    setResources(parseResources(await response.json()));
    setAuditEvents([]);
    setDataSource("demo");
  }, []);

  const loadLive = useCallback(async (activeSession: Session) => {
    const [user, inventory] = await Promise.all([
      getCurrentUser(activeSession.token),
      getInventory(activeSession.token),
    ]);
    const updatedSession = { token: activeSession.token, user };
    setSession(updatedSession);
    saveSession(updatedSession);
    setResources(inventory);
    setDataSource("live");
    setAuditEvents(user.role === "admin" ? await getAudit(activeSession.token) : []);
  }, []);

  const returnToDemo = useCallback(
    async (message?: string) => {
      clearSession();
      setSession(null);
      if (message) setNotice({ tone: "error", message });
      await loadDemo();
    },
    [loadDemo],
  );

  const handleFailure = useCallback(
    async (error: unknown, fallback: string) => {
      if (error instanceof ApiError && error.status === 401) {
        await returnToDemo("Your session expired. The dashboard returned to safe demo mode.");
        return;
      }
      setNotice({ tone: "error", message: error instanceof Error ? error.message : fallback });
    },
    [returnToDemo],
  );

  const refresh = useCallback(async () => {
    setLoading(true);
    setNotice(null);
    try {
      const available = await checkApi();
      setApiStatus(available ? "available" : "unavailable");
      if (available && session) await loadLive(session);
      else await loadDemo();
    } catch (error) {
      await handleFailure(error, "The dashboard could not be refreshed");
    } finally {
      setLoading(false);
    }
  }, [handleFailure, loadDemo, loadLive, session]);

  const signIn = useCallback(
    async (username: string, password: string) => {
      setLoading(true);
      setNotice(null);
      try {
        const token = await login(username, password);
        const user = await getCurrentUser(token);
        await loadLive({ token, user });
        setApiStatus("available");
        setNotice({ tone: "success", message: `Signed in as ${user.username} (${user.role}).` });
      } catch (error) {
        await handleFailure(error, "Sign-in failed");
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [handleFailure, loadLive],
  );

  const signOut = useCallback(async () => {
    setNotice({ tone: "info", message: "Signed out. Demo data is active." });
    await returnToDemo();
  }, [returnToDemo]);

  const operate = useCallback(
    async (intent: OperationIntent): Promise<Resource | null> => {
      if (!session || session.user.role !== "admin") return null;
      setLoading(true);
      setNotice(null);
      try {
        const result = await operateResource(session.token, intent.resource.id, intent.action);
        setResources((current) => current.map((item) => (item.id === result.resource.id ? result.resource : item)));
        setAuditEvents(await getAudit(session.token));
        setNotice({ tone: "success", message: `${intent.action} completed for ${intent.resource.name}.` });
        return result.resource;
      } catch (error) {
        await handleFailure(error, "The operation failed");
        return null;
      } finally {
        setLoading(false);
      }
    },
    [handleFailure, session],
  );

  useEffect(() => {
    void refresh();
  }, []); // Initial connectivity check only; later refreshes are explicit.

  return {
    apiStatus,
    auditEvents,
    dataSource,
    loading,
    notice,
    operate,
    refresh,
    resources,
    session,
    signIn,
    signOut,
  };
}
