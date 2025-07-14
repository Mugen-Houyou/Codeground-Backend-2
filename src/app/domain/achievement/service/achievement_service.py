from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.app.domain.achievement.crud import achievement_crud
from src.app.models.models import Achievement, UserAchievement, AchievementTriggerType


async def check_and_unlock_achievements(
    db: Session,
    user_id: int,
    trigger_type: AchievementTriggerType,
    current_value: int,
) -> None:
    achievements: list[Achievement] = achievement_crud.get_achievements_by_type(
        db,
        trigger_type,
    )
    for ach in achievements:
        if ach.parameter is not None and current_value >= ach.parameter:
            existing = achievement_crud.get_user_achievement(
                db,
                user_id,
                ach.achievement_id,
            )
            if not existing:
                ua = achievement_crud.create_user_achievement(
                    db,
                    user_id,
                    ach.achievement_id,
                )
                ua.current_value = current_value
                ua.obtained_at = datetime.now(timezone.utc)
    db.commit()


async def handle_achievement_event(
    db: Session,
    user_id: int,
    trigger_type: AchievementTriggerType,
    # N번 안에 풀기, 빨리 풀기 등 추가 파라미터가 필요한 경우를 대비
    **kwargs,
) -> None:
    current_value = 0
    if trigger_type == AchievementTriggerType.TOTAL_WIN:
        current_value = achievement_crud.get_total_wins(db, user_id)
    elif trigger_type == AchievementTriggerType.TOTAL_LOSS:
        current_value = achievement_crud.get_total_losses(db, user_id)
    elif trigger_type == AchievementTriggerType.TOTAL_DRAW:
        current_value = achievement_crud.get_total_draws(db, user_id)
    elif trigger_type == AchievementTriggerType.CONSECUTIVE_WIN:
        current_value = achievement_crud.get_consecutive_wins(db, user_id)
    elif trigger_type == AchievementTriggerType.CONSECUTIVE_LOSS:
        current_value = achievement_crud.get_consecutive_losses(db, user_id)

    # 다른 트리거 타입에 대한 값 계산 로직 추가
    # elif trigger_type == AchievementTriggerType.PROBLEM_SOLVED:
    #     current_value = achievement_crud.get_total_problems_solved(db, user_id)

    if current_value > 0:
        await check_and_unlock_achievements(
            db,
            user_id,
            trigger_type,
            current_value,
        )



def get_user_achievements(db: Session, user_id: int) -> list[UserAchievement]:
    return achievement_crud.list_user_achievements(db, user_id)