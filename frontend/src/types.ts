export type UserRole = "viewer" | "admin";
export type ResourceType = "container" | "vm";
export type ResourceStatus = "running" | "stopped" | "planned" | "error" | "unknown";
export type ResourceAction = "start" | "stop" | "restart";
export type ApiStatus = "checking" | "available" | "unavailable";
export type DataSource = "demo" | "live";

export type User = {
  id: number;
  username: string;
  role: UserRole;
  is_active: boolean;
};

export type Session = {
  token: string;
  user: User;
};

export type Resource = {
  id: string;
  name: string;
  type: ResourceType;
  status: ResourceStatus;
  description: string;
  tags: string[];
  environment: string;
  host_name: string;
  image_name: string | null;
  health_status: string | null;
  allowed_actions: ResourceAction[];
  created_utc: string;
  updated_utc: string;
};

export type AuditEvent = {
  id: number;
  actor_id: number;
  event_type: string;
  resource_id: string | null;
  action_request_id: number | null;
  outcome: string;
  source_ip: string | null;
  detail: string;
  created_at: string;
};

export type OperationResult = {
  request_id: number;
  resource: Resource;
  action: ResourceAction;
  status: string;
};

export type OperationIntent = {
  resource: Resource;
  action: ResourceAction;
};

export type Notice = {
  tone: "info" | "success" | "error";
  message: string;
};
