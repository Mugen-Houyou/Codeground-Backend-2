from sqlalchemy.orm import Session
from src.app.models.models import User, UserMmr, UserRole
from src.app.domain.auth.schemas import auth_schemas as schemas
from typing import Optional


async def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


async def get_by_email(db: Session, email: str) -> bool:
    search_email = db.query(User).filter(User.email == email).first()
    return True if search_email else False


async def get_by_nickname(db: Session, nickname: str) -> bool:
    return db.query(User).filter(User.nickname == nickname).first() is not None


async def join_user(db: Session, sign_up_request: schemas.SignupRequest) -> User:
    new_user = User(
        email=str(sign_up_request.email),
        username=sign_up_request.username,
        nickname=sign_up_request.nickname,
        role=UserRole.USER,
        password=sign_up_request.password,
        use_lang=sign_up_request.use_lang,
    )
    db.add(new_user)
    db.flush()
    db.refresh(new_user)

    mmr_row = UserMmr(user_id=new_user.user_id, rating=1000)
    db.add(mmr_row)

    return new_user
