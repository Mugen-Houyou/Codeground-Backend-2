from sqlalchemy.orm import Session
from src.app.models.models import CheatReport

def create_report(
    db: Session,
    game_id: int | None,
    reason: str,
    description: str,
    video_path: str
) -> CheatReport:
    report = CheatReport(
        game_id=game_id,
        reason=reason,
        description=description,
        video_path=video_path
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report