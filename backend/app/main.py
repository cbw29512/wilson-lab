from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import Base, SessionLocal, engine
from .middleware import RequestContextMiddleware
from .rate_limit import LoginRateLimiter
from .routers import auth, resources, system
from .runtime import build_runtime
from .security import seed_demo_users

settings = get_settings()
is_production = settings.environment.lower() == "production"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as database:
        seed_demo_users(database, settings)
    app.state.runtime = build_runtime(settings)
    app.state.login_limiter = LoginRateLimiter(
        attempt_limit=settings.login_attempt_limit,
        window_seconds=settings.login_window_seconds,
    )
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.8.0",
    description="Secure, allowlisted control plane for the Wilson Lab sandbox.",
    lifespan=lifespan,
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(RequestContextMiddleware)
app.include_router(system.router)
app.include_router(auth.router)
app.include_router(resources.router)
