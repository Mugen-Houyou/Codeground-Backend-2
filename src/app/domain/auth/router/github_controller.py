from typing import Annotated
from fastapi import APIRouter, Depends, Response
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from src.app.core.database import get_db
from src.app.core.token import create_access_token
from src.app.domain.auth.service.github_service import get_github_auth_url, handle_github_callback
from src.app.config.config import settings
from src.app.domain.auth.router.auth_controller import get_cookie_options

router = APIRouter(prefix="/auth/github")

DB = Annotated[Session, Depends(get_db)]


@router.get("/login")
async def github_login():
    redirect_url = get_github_auth_url()
    return {"redirect_url": redirect_url}


@router.get("/callback")
async def github_callback(code: str, db: DB):
    result = await handle_github_callback(code, db)

    if isinstance(result, RedirectResponse):
        return result  # 이메일 중복 등은 여전히 Redirect로 처리

    user, is_new_user = result
    access_token = create_access_token(subject=user.email)  # ✅ user.email → user.user_id

    response = JSONResponse(content={"message": "Login successful", "is_new_user": is_new_user})

    secure, samesite, domain, http_only = get_cookie_options()
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=http_only,
        secure=secure,
        samesite=samesite,
        path="/",
        max_age=60 * 60 * 24,
        domain=domain,
    )
    return response

