import secrets
import asyncio
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.app.domain.auth.crud import auth_crud as crud
from src.app.domain.auth.schemas import auth_schemas as schemas
from src.app.core.password import get_password_hash, verify_password
from src.app.utils.email import send_email

reset_code_store = {}


async def check_duplicate_email(db: Session, email: str) -> None:
    if await crud.get_by_email(db=db, email=email):
        raise HTTPException(detail="이미 사용 중인 이메일입니다.", status_code=status.HTTP_400_BAD_REQUEST)


async def check_duplicate_nickname(db: Session, nickname: str) -> None:
    if await crud.get_by_nickname(db, nickname):
        raise HTTPException(detail="이미 사용 중인 닉네임입니다.", status_code=status.HTTP_400_BAD_REQUEST)


async def join(db: Session, sign_up_request: schemas.SignupRequest) -> schemas.SignupResponse:
    sign_up_request.password = get_password_hash(sign_up_request.password)
    new_user = await crud.join_user(db=db, sign_up_request=sign_up_request)

    if not new_user:
        raise HTTPException(detail="Fail Sign Up User", status_code=400)

    return schemas.SignupResponse.model_validate(new_user)


async def authenticate_user(db: Session, email: str, password: str) -> schemas.LoginUserDto:
    user = await crud.get_user_by_email(db=db, email=email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User Data")

    if not await verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Password")

    return schemas.LoginUserDto.model_validate(user)


def check_email_exists(db: Session, email: str) -> bool:
    return asyncio.run(crud.get_by_email(db, email)) is not None


def check_nickname_exists(db: Session, nickname: str) -> bool:
    return asyncio.run(crud.get_by_nickname(db, nickname)) is not None


async def send_reset_password_email(db: Session, email: str):
    user = await crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="등록되지 않은 이메일입니다.")

    code = secrets.token_hex(3)
    expires = datetime.now(timezone.utc) + timedelta(minutes=10)
    reset_code_store[email] = (code, expires)

    await send_email(to=email, subject="비밀번호 초기화", body=f"인증코드: {code}")


async def verify_reset_code(email: str, code: str):
    stored = reset_code_store.get(email)
    if not stored:
        raise HTTPException(status_code=400, detail="인증 요청이 없습니다.")
    if stored[0] != code:
        raise HTTPException(status_code=400, detail="잘못된 인증 코드입니다.")
    if stored[1] < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="인증 코드가 만료되었습니다.")


async def reset_password(db: Session, email: str, code: str, new_password: str):
    await verify_reset_code(email, code)

    user = await crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="유저 없음")

    user.password = get_password_hash(new_password)
    db.add(user)
    db.commit()
    reset_code_store.pop(email, None)
