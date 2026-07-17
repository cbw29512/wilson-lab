from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import desc, select

from .config import get_settings
from .database import Base, SessionLocal, engine
from .dependencies import AdminUser, CurrentUser, Database, Runtime
from .models import ActionRequest, ActionStatus, AuditEvent
from .runtime import RuntimeError, build_runtime
from .schemas import (
    AuditEventPublic,
    OperationResult,
    Resource,
    ResourceOperation,
    Token,
    UserPublic,
)
from .security import authenticate_user, create_access_token, seed_demo_users

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as database:
        seed_demo_users(database, settings)
    app.state.runtime = build_runtime(settings)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Secure, allowlisted control plane for the Wilson Lab sandbox.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment, "runtime": settings.runtime_mode}


@app.post("/api/v1/auth/token", response_model=Token)
def login(form: OAuth2PasswordRequestForm, database: Database) -> Token:
    user = authenticate_user(database, form.username, form.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user, settings))


@app.get("/api/v1/auth/me", response_model=UserPublic)
def current_user(user: CurrentUser) -> UserPublic:
    return UserPublic.model_validate(user)


@app.get("/api/v1/inventory", response_model=list[Resource])
def inventory(_: CurrentUser, runtime: Runtime) -> list[Resource]:
    return runtime.list_resources()


@app.get("/api/v1/inventory/{resource_id}", response_model=Resource)
def resource_detail(resource_id: str, _: CurrentUser, runtime: Runtime) -> Resource:
    try:
        return runtime.get_resource(resource_id)
    except RuntimeError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@app.post("/api/v1/resources/{resource_id}/operations", response_model=OperationResult)
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


@app.get("/api/v1/audit", response_model=list[AuditEventPublic])
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
