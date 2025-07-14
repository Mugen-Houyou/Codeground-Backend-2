from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.app.core.database import get_db
from src.app.core.security import get_current_user
from src.app.domain.achievement.service import achievement_service
from src.app.models.models import User

router = APIRouter(prefix="/achievements", tags=["achievement"])


@router.get("/me")
async def get_my_achievements(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    achievements = achievement_service.get_user_achievements(
        db,
        current_user.user_id,
    )
    return achievements
