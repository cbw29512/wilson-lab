from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from ..config import get_settings
from ..dependencies import CurrentUser, Database
from ..rate_limit import LoginRateLimiter, RateLimitDecision
from ..schemas import Token, UserPublic
from ..security import authenticate_user, create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
settings = get_settings()


def client_identity(request: Request, username: str) -> str:
    client_ip = request.client.host if request.client else "unknown"
    return LoginRateLimiter.key(client_ip, username)


def reject_rate_limited(decision: RateLimitDecision) -> None:
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Too many login attempts. Try again later.",
        headers={"Retry-After": str(decision.retry_after)},
    )


@router.post("/token", response_model=Token)
def login(
    request: Request,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    database: Database,
) -> Token:
    limiter: LoginRateLimiter = request.app.state.login_limiter
    key = client_identity(request, form.username)
    decision = limiter.check(key)
    if not decision.allowed:
        reject_rate_limited(decision)

    user = authenticate_user(database, form.username, form.password)
    if not user:
        decision = limiter.register_failure(key)
        if not decision.allowed:
            reject_rate_limited(decision)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    limiter.reset(key)
    return Token(access_token=create_access_token(user, settings))


@router.get("/me", response_model=UserPublic)
def current_user(user: CurrentUser) -> UserPublic:
    return UserPublic.model_validate(user)
