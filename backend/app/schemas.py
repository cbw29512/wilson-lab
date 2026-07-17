from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from .models import ActionName, ActionStatus, UserRole


class ResourceType(StrEnum):
    CONTAINER = "container"
    VM = "vm"


class ResourceStatus(StrEnum):
    RUNNING = "running"
    STOPPED = "stopped"
    PLANNED = "planned"
    ERROR = "error"
    UNKNOWN = "unknown"


class Resource(BaseModel):
    id: str
    name: str
    type: ResourceType = ResourceType.CONTAINER
    status: ResourceStatus
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    environment: str = "sandbox"
    host_name: str = "wilson-lab"
    image_name: str | None = None
    health_status: str | None = None
    allowed_actions: list[ActionName] = Field(default_factory=list)
    created_utc: datetime
    updated_utc: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: UserRole
    is_active: bool


class ResourceOperation(BaseModel):
    action: ActionName
    confirmed: bool = False


class OperationResult(BaseModel):
    request_id: int
    resource: Resource
    action: ActionName
    status: ActionStatus


class AuditEventPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_id: int
    event_type: str
    resource_id: str | None
    action_request_id: int | None
    outcome: str
    source_ip: str | None
    detail: str
    created_at: datetime
