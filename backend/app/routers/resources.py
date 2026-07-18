from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import desc, select

from ..dependencies import AdminUser, CurrentUser, Database, Runtime
from ..models import ActionRequest, ActionStatus, AuditEvent
from ..runtime import RuntimeError
from ..schemas import AuditEventPublic, OperationResult, Resource, ResourceOperation

router = APIRouter(prefix="/api/v1", tags=["resources"])


@router.get("/inventory", response_model=list[Resource])
def inventory(_: CurrentUser, runtime: Runtime) -> list[Resource]:
    try:
        return runtime.list_resources()
    except RuntimeError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error


@router.get("/inventory/{resource_id}", response_model=Resource)
def resource_detail(resource_id: str, _: CurrentUser, runtime: Runtime) -> Resource:
    try:
        return runtime.get_resource(resource_id)
    except RuntimeError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.post("/resources/{resource_id}/operations", response_model=OperationResult)
def operate_resource(
    resource_id: str,
    operation: ResourceOperation,
    request: Request,
    user: AdminUser,
    database: Database,
    runtime: Runtime,
) -> OperationResult:
    if not operation.confirmed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Explicit confirmation is required",
        )

    action_request = ActionRequest(
        resource_id=resource_id,
        action=operation.action,
        status=ActionStatus.PENDING,
        requested_by_id=user.id,
    )
    database.add(action_request)
    database.commit()
    database.refresh(action_request)

    try:
        resource = runtime.apply(resource_id, operation.action)
        action_request.status = ActionStatus.SUCCEEDED
        outcome = ActionStatus.SUCCEEDED
        detail = f"{operation.action} completed for managed resource"
    except RuntimeError as error:
        action_request.status = ActionStatus.FAILED
        action_request.error_message = str(error)
        outcome = ActionStatus.FAILED
        detail = str(error)
        resource = None

    action_request.completed_at = datetime.now(timezone.utc)
    database.add(
        AuditEvent(
            actor_id=user.id,
            event_type="resource.operation",
            resource_id=resource_id,
            action_request_id=action_request.id,
            outcome=outcome,
            source_ip=request.client.host if request.client else None,
            detail=detail,
        )
    )
    database.commit()

    if resource is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)

    return OperationResult(
        request_id=action_request.id,
        resource=resource,
        action=operation.action,
        status=ActionStatus.SUCCEEDED,
    )


@router.get("/audit", response_model=list[AuditEventPublic])
def audit_events(
    _: AdminUser,
    database: Database,
    limit: int = 50,
) -> list[AuditEventPublic]:
    safe_limit = min(max(limit, 1), 200)
    events = database.scalars(
        select(AuditEvent).order_by(desc(AuditEvent.created_at)).limit(safe_limit)
    ).all()
    return [AuditEventPublic.model_validate(event) for event in events]
